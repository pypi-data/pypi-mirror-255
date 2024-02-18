#!/usr/bin/env python

from __future__ import division, print_function
import os
import argparse
import importlib.util
import logging
import faulthandler
import tqdm
import pandas as pd
from pathlib import Path

import torch
import torch.backends.cudnn as cudnn
from torch.multiprocessing import Queue, Process
from torch.utils.data import DataLoader

import gammalearn.datasets
from gammalearn.version import __version__ as _version
from gammalearn.utils import (get_dataset_geom, find_datafiles, post_process_data,
                              write_dl2_file, prepare_dict_of_tensors, inject_geometry_into_parameters)
from gammalearn.data_handlers import create_dataset_worker
from gammalearn.datasets import WrongGeometryError
from gammalearn.experiment_runner import LitGLearnModule, Experiment
from gammalearn.logging import LOGGING_CONFIG


faulthandler.enable()


def create_dataset(file_queue: Queue, dl1_queue: Queue, dataset_class: gammalearn.datasets.BaseLSTDataset,
                   dataset_parameters: dict) -> None:
    """
    Create the datasets and fill the correspond queue.

    Parameters
    ----------
    file_queue: (Queue) The queue containing the file names of the dl1 folder.
    dl1_queue: (Queue) The queue containing the datasets.
    dataset_class: (gammalearn.datasets.BaseLSTDataset) the dataset class as specified in the experiment settings file.
    dataset_parameters: (dict) The dataset parameters as specified in the experiment settings file.
    """
    while True:
        if not file_queue.empty():
            file = file_queue.get()
            dataset = create_dataset_worker(file, dataset_class, train=False, **dataset_parameters)
            dl1_queue.put(dataset)


def dl2_filename(dl1_filename):
    return os.path.basename(dl1_filename).replace('dl1', 'dl2')


def build_argparser():
    """
    Construct main argument parser for the ``gl_dl1_to_dl2`` script

    :return:
    argparser: `argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        description="Convert DL1 files to DL2 files using a trained model."
    )
    parser.add_argument('settings', type=Path, help='Path to the experiment settings file')
    parser.add_argument('checkpoint', type=Path, help='Path to the checkpoint file to load')
    parser.add_argument('dl1', type=Path, help='Directory path to the dl1 files')
    parser.add_argument('dl2', type=Path,  help='Directory path to write the dl2 files')
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--max-queue', type=int, default=20)
    parser.add_argument('--preprocess-workers', type=int, default=4)
    parser.add_argument('--dataloader-workers', type=int, default=4)
    parser.add_argument('--version', action='version', version=_version)
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing output files')

    return parser


def main():
    # For better performance (if the input size does not vary from a batch to another)
    cudnn.benchmark = True

    parser = build_argparser()
    args = parser.parse_args()
    configuration_file = args.settings

    # Create DL2 directory and logs directory
    dl2_path = args.dl2
    logs_dir = dl2_path.joinpath('logs')
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Get dl1 files
    dl1_file_list = find_datafiles([args.dl1])
    dl2_outputs = [dl2_path.joinpath(dl2_filename(dl1file)) for dl1file in dl1_file_list]
    if not args.overwrite and any([dl2file.exists() for dl2file in dl2_outputs]):
        raise FileExistsError(f'Output files already exists in {dl2_path}. Use --overwrite to overwrite existing files.')

    # Update logging config
    LOGGING_CONFIG['loggers']['gammalearn']['level'] = 'INFO'
    LOGGING_CONFIG['handlers']['file'] = {
        'class': 'logging.FileHandler',
        'filename': logs_dir.joinpath('dl1_to_dl2.log'),
        'mode': 'a',
        'formatter': 'detailed_info'
    }
    LOGGING_CONFIG['loggers']['gammalearn']['handlers'].append('file')
    logger = logging.getLogger('gammalearn')
    logging.config.dictConfig(LOGGING_CONFIG)

    # Load experiment
    logger.info(f'load settings from {configuration_file}')
    spec = importlib.util.spec_from_file_location("settings", configuration_file)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    experiment = Experiment(settings)
    experiment.dataset_parameters['transform'] = experiment.data_module_test.get('transform', None)

    # Prepare data
    logger.info('prepare data')

    # Load file names
    logger.info('find dl1 files and populate file queue')
    file_queue = Queue()
    for file in tqdm.tqdm(dl1_file_list):
        file_queue.put(file)

    # Create a group of parallel writers and start them
    dl1_queue = Queue(args.max_queue)
    processes = []
    for rank in range(args.preprocess_workers):
        p = Process(target=create_dataset, args=(file_queue,
                                                 dl1_queue,
                                                 experiment.dataset_class,
                                                 experiment.dataset_parameters))
        p.start()
        processes.append(p)

    model = None

    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    logger.info('start processing dl1 datasets')
    for _ in tqdm.tqdm(dl1_file_list):
        dataset = dl1_queue.get()
        dataloader = DataLoader(dataset, batch_size=args.batch_size, num_workers=args.dataloader_workers)

        if model is None:
            logger.info('Load model')
            geometries = []
            get_dataset_geom(dataset, geometries)
            # Testing if all geometries are equal
            if len(set(geometries)) != 1:
                raise WrongGeometryError("There are different geometries in the train and the test datasets")
            experiment.net_parameters_dic = inject_geometry_into_parameters(experiment.net_parameters_dic, geometries[0])
            # Load checkpoint
            checkpoint_path = args.checkpoint
            model = LitGLearnModule.load_from_checkpoint(checkpoint_path, experiment=experiment, strict=False)
            model.eval()
            model.to(device)

        test_data = {'output': [], 'dl1_params': []}

        for batch in tqdm.tqdm(dataloader):
            with torch.no_grad():
                images = batch['image'].to(device)
                output = model(images)

            for k, v in output.items():
                output[k] = v.cpu()

            test_data['output'].append(output)
            test_data['dl1_params'].append(batch['dl1_params'])

        merged_outputs = pd.concat([pd.DataFrame(prepare_dict_of_tensors(output))
                                    for output in test_data['output']], ignore_index=True)
        merged_dl1_params = pd.concat([pd.DataFrame(prepare_dict_of_tensors(dl1))
                                       for dl1 in test_data['dl1_params']], ignore_index=True)
        dl2_params = post_process_data(merged_outputs, merged_dl1_params, settings.dataset_parameters)

        output_path = dl2_path.joinpath(dl2_filename(dataset.hdf5_file_path))
        if os.path.exists(output_path) and args.overwrite:
            os.remove(output_path)
        write_dl2_file(dl2_params, dataset, output_path)

    logger.info('All files processed')
    for p in processes:
        p.terminate()


if __name__ == '__main__':
    main()

import logging
import torch.multiprocessing as mp
from functools import partial
import tqdm
import collections

from pytorch_lightning import LightningDataModule
import torch
from torch.utils.data import DataLoader, Dataset, ConcatDataset, Subset
from torchvision import transforms
from gammalearn.datasets import VisionDomainAdaptationDataset, GlearnDomainAdaptationDataset

from gammalearn import utils as utils
from gammalearn.logging import LOGGING_CONFIG


def create_dataset_worker(file,
                          dataset_class,
                          train,
                          **kwargs):
    torch.set_num_threads(1)
    # Reload logging config (lost by spawn)
    logging.config.dictConfig(LOGGING_CONFIG)

    if utils.is_datafile_healthy(file):
        dataset = dataset_class(file, train=train, **kwargs)
        if kwargs.get('image_filter') is not None:
            dataset.filter_image(kwargs.get('image_filter'))
        if kwargs.get('event_filter') is not None:
            dataset.filter_event(kwargs.get('event_filter'))
        if len(dataset) > 0:
            return dataset


def create_datasets(datafiles_list, experiment, train=True, **kwargs):
    """
    Create datasets from datafiles list, data are loaded in memory.
    Parameters
    ----------
    datafiles (List) : files to load data from
    experiment (Experiment): the experiment

    Returns
    -------
    Datasets
    """

    logger = logging.getLogger('gammalearn')
    assert datafiles_list, 'The data file list is empty !'

    logger.info('length of data file list : {}'.format(len(datafiles_list)))
    # We get spawn context because fork can cause deadlock in sub-processes
    # in multi-threaded programs (especially with logging)
    ctx = mp.get_context('spawn')
    if experiment.preprocessing_workers > 0:
        num_workers = experiment.preprocessing_workers
    else:
        num_workers = 1
    pool = ctx.Pool(processes=num_workers)
    datasets = list(tqdm.tqdm(pool.imap(partial(create_dataset_worker,
                                                dataset_class=experiment.dataset_class,
                                                train=train,
                                                **kwargs),
                                        datafiles_list),
                              total=len(datafiles_list),
                              desc='Load data files'
                              )
                    )

    return datasets


def split_dataset(datasets, ratio):
    """Split a list of datasets into a train and a validation set
    Parameters
    ----------
    datasets (list of Dataset): the list of datasets
    ratio (float): the ratio of data for validation

    Returns
    -------
    train set, validation set

    """
    # Creation of subset train and test
    assert 1 > ratio > 0, 'Validating ratio must be greater than 0 and smaller than 1.'

    train_max_index = int(len(datasets) * (1 - ratio))
    shuffled_indices = torch.randperm(len(datasets)).numpy()
    assert isinstance(datasets, Dataset)
    train_datasets = Subset(datasets, shuffled_indices[:train_max_index])
    val_datasets = Subset(datasets, shuffled_indices[train_max_index:])

    return train_datasets, val_datasets


def balance_datasets(source_datasets, target_datasets):
    max_index = min(len(source_datasets), len(target_datasets))
    shuffled_indices_source = torch.randperm(len(source_datasets)).numpy()
    shuffled_indices_target = torch.randperm(len(target_datasets)).numpy()

    source_datasets = Subset(source_datasets, shuffled_indices_source[:max_index])
    target_datasets = Subset(target_datasets, shuffled_indices_target[:max_index])

    return source_datasets, target_datasets


class BaseDataModule(LightningDataModule):
    """
    Create datasets and dataloaders.
    Parameters
    ----------
    experiment (Experiment): the experiment

    Returns
    -------
    """
    def __init__(self, experiment):
        super().__init__()
        self.experiment = experiment
        self.logger = logging.getLogger(__name__)
        self.train_set = None
        self.val_set = None
        self.test_sets = None  # List
        self.collate_fn = torch.utils.data.default_collate

    def setup(self, stage=None):
        """
        In the case that the train and the test data modules are different, two setup functions are defined in order to
         prevent from loading data twice.
        """
        self.setup_train()
        self.setup_test()

    def setup_train(self):
        """
        This function is used if train is set to True in experiment setting file
        """
        self.logger.info('Start creating datasets')
        self.logger.info('look for data files')

        # Creation of the global train/val dataset
        datasets = self.get_dataset(train=True)
        assert datasets, 'Dataset is empty !'

        # Creation of subsets train and validation
        train_datasets, val_datasets = split_dataset(datasets, self.experiment.validating_ratio)

        self.train_set = train_datasets
        self.logger.info('training set length : {}'.format(len(self.train_set)))

        self.val_set = val_datasets
        try:
            assert len(self.val_set) > 0
        except AssertionError as e:
            self.logger.exception('Validating set must contain data')
            raise e
        self.logger.info('validating set length : {}'.format(len(self.val_set)))

    def setup_test(self):
        """
        This function is used if test is set to True in experiment setting file.
        If no data module test is provided, test is completed on the validation set.
        If neither a data module test nor a validation set is provided, an error will be raised.
        """
        if self.experiment.data_module_test is not None:
            # Look for specific data parameters
            if self.experiment.test_dataset_parameters is not None:
                self.experiment.dataset_parameters.update(self.experiment.test_dataset_parameters)

            # Creation of the test datasets
            self.test_sets = self.get_dataset(train=False)
        else:  # Test is set to False in experiment setting file
            assert self.val_set is not None, 'Test is required but no test file is provided and val_set is None'
            self.test_sets = [self.val_set]
        self.logger.info('test set length : {}'.format(torch.tensor([len(t) for t in self.test_sets]).sum()))

    def train_dataloader(self):
        training_loader = DataLoader(self.train_set,
                                     batch_size=self.experiment.batch_size,
                                     shuffle=True,
                                     drop_last=True,
                                     num_workers=self.experiment.dataloader_workers,
                                     pin_memory=self.experiment.pin_memory,
                                     collate_fn=self.collate_fn)
        self.logger.info('training loader length : {} batches'.format(len(training_loader)))
        return training_loader

    def val_dataloader(self):
        validating_loader = DataLoader(self.val_set,
                                       batch_size=self.experiment.batch_size,
                                       shuffle=False,
                                       num_workers=self.experiment.dataloader_workers,
                                       drop_last=True,
                                       pin_memory=self.experiment.pin_memory,
                                       collate_fn=self.collate_fn)
        self.logger.info('validating loader length : {} batches'.format(len(validating_loader)))
        return validating_loader

    def test_dataloaders(self):
        test_loaders = [DataLoader(test_set, batch_size=self.experiment.test_batch_size, shuffle=False,
                                   drop_last=False, num_workers=self.experiment.dataloader_workers)
                        for test_set in self.test_sets]
        self.logger.info('test loader length : {} data loader(s)'.format(len(test_loaders)))
        self.logger.info('test loader length : {} batches'.format(torch.tensor([len(t) for t in test_loaders]).sum()))
        return test_loaders

    def get_dataset(self, train):
        """
        DataModule-specific method to be overwritten to load the dataset.
        """
        return NotImplementedError

    def get_collate_fn(self):
        numpy_type_map = {
            'float64': torch.DoubleTensor,
            'float32': torch.FloatTensor,
            'float16': torch.HalfTensor,
            'int64': torch.LongTensor,
            'int32': torch.IntTensor,
            'int16': torch.ShortTensor,
            'int8': torch.CharTensor,
            'uint8': torch.ByteTensor,
        }

        def collate_fn(batch):
            """
            Puts each data field into a tensor with outer dimension batch size. From:
            https://github.com/hughperkins/pytorch-pytorch/blob/c902f1cf980eef27541f3660c685f7b59490e744/torch/utils/data/dataloader.py#L91
            """
            error_msg = "batch must contain tensors, numbers, dicts or lists; found {}"
            elem_type = type(batch[0])
            if torch.is_tensor(batch[0]):
                out = None
                return torch.stack(batch, 0, out=out)
            elif elem_type.__module__ == 'numpy' and elem_type.__name__ != 'str_' \
                    and elem_type.__name__ != 'string_':
                elem = batch[0]
                if elem_type.__name__ == 'ndarray':
                    return torch.stack([torch.from_numpy(b) for b in batch], 0)
                if elem.shape == ():  # scalars
                    py_type = float if elem.dtype.name.startswith('float') else int
                    return numpy_type_map[elem.dtype.name](list(map(py_type, batch)))
            elif isinstance(batch[0], int):
                return torch.LongTensor(batch)
            elif isinstance(batch[0], float):
                return torch.DoubleTensor(batch)
            elif isinstance(batch[0], (str, bytes)):
                return batch
            elif isinstance(batch[0], collections.Mapping):
                # If MC and real data in target, find the common keys
                common_keys = set(batch[0].keys())
                for d in batch[1:]:
                    common_keys.intersection_update(d.keys())
                return {key: collate_fn([d[key] for d in batch]) for key in common_keys}
            elif isinstance(batch[0], collections.Sequence):
                transposed = zip(*batch)
                return [collate_fn(samples) for samples in transposed]

            raise TypeError((error_msg.format(type(batch[0]))))
        return collate_fn


class GLearnDataModule(BaseDataModule):
    def __init__(self, experiment):
        super().__init__(experiment)

    def get_dataset(self, train):
        max_files = self.experiment.train_files_max_number if train else self.experiment.test_files_max_number
        data_module = utils.fetch_data_module_settings(self.experiment, train=train, domain=None)
        dataset = self.get_glearn_dataset_from_path(data_module, train, domain=None, max_files=max_files)

        return dataset

    def get_glearn_dataset_from_path(self, data_module, train, domain=None, max_files=None):
        if max_files is None:
            max_files = -1
        else:
            if isinstance(max_files, dict):
                max_files = max_files.get(domain, -1)

        file_list = utils.find_datafiles(data_module['paths'], max_files)
        file_list = list(file_list)
        file_list.sort()

        datasets = create_datasets(file_list, self.experiment, train=train, **{'domain': domain}, **data_module,
                                   **self.experiment.dataset_parameters)

        if train:
            # Check the dataset list heterogeneity (e.g. simu and real data in target)
            if not(all([dset.simu for dset in datasets]) or not any([dset.simu for dset in datasets])):
                self.collate_fn = self.get_collate_fn()
            return ConcatDataset(datasets)
        else:
            if self.experiment.merge_test_datasets:
                particle_dict = {}

                for dset in datasets:
                    if dset.simu:
                        particle_type = dset.dl1_params['mc_type'][0]

                        if particle_type in particle_dict:
                            particle_dict[particle_type].append(dset)
                        else:
                            particle_dict[particle_type] = [dset]
                    else:
                        if 'real_list' in particle_dict:
                            particle_dict['real_list'].append(dset)
                        else:
                            particle_dict['real_list'] = [dset]

                return [ConcatDataset(dset) for dset in particle_dict.values()]
            else:
                return datasets


class GLearnDomainAdaptationDataModule(GLearnDataModule):
    def __init__(self, experiment):
        super().__init__(experiment)
        self.dataset_balancing = experiment.dataset_parameters.get('dataset_balancing', True)

    def get_dataset(self, train):
        max_files = self.experiment.train_files_max_number if train else self.experiment.test_files_max_number
        data_module_source = utils.fetch_data_module_settings(self.experiment, train=train, domain='source')
        data_module_target = utils.fetch_data_module_settings(self.experiment, train=train, domain='target')
        source_datasets = self.get_glearn_dataset_from_path(data_module_source,
                                                            train,
                                                            domain='source',
                                                            max_files=max_files)
        target_datasets = self.get_glearn_dataset_from_path(data_module_target,
                                                            train,
                                                            domain='target',
                                                            max_files=max_files)

        if self.dataset_balancing:
            source_datasets, target_datasets = balance_datasets(source_datasets, target_datasets)

        return GlearnDomainAdaptationDataset(source_datasets, target_datasets)


class VisionDataModule(BaseDataModule):
    """
    Create datasets and dataloaders.
    Parameters
    ----------
    experiment (Experiment): the experiment

    Returns
    -------
    """
    def __init__(self, experiment):
        super().__init__(experiment)

    def get_dataset(self, train):
        max_files = self.experiment.train_files_max_number if train else self.experiment.test_files_max_number
        data_module = utils.fetch_data_module_settings(self.experiment, train=train, domain=None)
        dataset = self.get_dataset_from_path(data_module, train=train, domain=None, max_files=max_files)

        return dataset

    def get_dataset_from_path(self, data_module, train, domain=None, max_files=None):
        datasets = self.experiment.dataset_class(
            paths=data_module['paths'],
            dataset_parameters=self.experiment.dataset_parameters,
            transform=data_module['transform'],
            target_transform=data_module['target_transform'],
            train=train,
            domain=domain,
            max_files=max_files,
            num_workers=self.experiment.preprocessing_workers,
        )

        return [datasets] if not train else datasets


class VisionDomainAdaptationDataModule(VisionDataModule):
    """
    Create datasets and dataloaders.
    Parameters
    ----------
    experiment (Experiment): the experiment

    Returns
    -------
    """
    def __init__(self, experiment):
        super().__init__(experiment)
        self.dataset_balancing = experiment.dataset_parameters.get('dataset_balancing', True)

    def get_dataset(self, train):
        max_files = self.experiment.train_files_max_number if train else self.experiment.test_files_max_number

        data_module_source = utils.fetch_data_module_settings(self.experiment, train=train, domain='source')
        data_module_target = utils.fetch_data_module_settings(self.experiment, train=train, domain='target')

        dataset_src = self.get_dataset_from_path(data_module_source, train=train, domain='source', max_files=max_files)
        dataset_trg = self.get_dataset_from_path(data_module_target, train=train, domain='target', max_files=max_files)

        if self.dataset_balancing:
            dataset_src, dataset_trg = balance_datasets(dataset_src, dataset_trg)

        return VisionDomainAdaptationDataset(dataset_src, dataset_trg)

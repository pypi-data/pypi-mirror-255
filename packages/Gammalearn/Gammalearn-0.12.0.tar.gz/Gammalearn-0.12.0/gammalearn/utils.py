import os
import logging
import collections
import json
import pkg_resources

import numpy as np
import tables
import torch
from ctapipe.image import tailcuts_clean, leakage_parameters, hillas_parameters
from ctaplot.ana import angular_separation_altaz
import random
import gammalearn.datasets
from . import version
from .constants import GAMMA_ID
from astropy.utils import deprecated
import pandas as pd
from pathlib import Path
from tables.scripts.ptrepack import copy_leaf
from lstchain.reco.utils import add_delta_t_key
from lstchain.io.io import dl2_params_lstcam_key
import gammalearn.version as gl_version
from pytorch_lightning.loggers import TensorBoardLogger, WandbLogger
from gammalearn.callbacks import LogModelParameters


class TrainerLogger:
    """
    The TrainerLogger class is used to define the logger used by the Pytorch Lightning Trainer.
    """
    def __init__(self) -> None:
        pass

    def setup(self, experiment, gl_lightning_module) -> None:
        return NotImplementedError
    
    def get_log_directory(self, experiment) -> str:
        return os.path.join(experiment.main_directory, 'runs')
    
    def get_run_directory(self, experiment) -> str:
        return os.path.join(self.get_log_directory(experiment), experiment.experiment_name)
    
    def create_directory(self, directory) -> None:
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chmod(directory, 0o775)


class TrainerTensorboardLogger(TrainerLogger):
    """
    The TrainerTensorboardLogger is a wrapper around the TensorBoardLogger class.
    It is used to define the logger used by the Pytorch Lightning Trainer, based on Tensorboard.
    """
    def __init__(self) -> None:
        super().__init__()
        self.type = 'TensorBoardLogger'

    def setup(self, experiment, gl_lightning_module) -> None:
        run_directory = self.get_run_directory(experiment)
        self.create_directory(run_directory)
        self.logger = TensorBoardLogger(self.get_log_directory(experiment), experiment.experiment_name)

    
class TrainerWandbLogger(TrainerLogger):
    """
    The TrainerWandbLogger is a wrapper around the WandbLogger class.
    It is used to define the logger used by the Pytorch Lightning Trainer, based on Weights and Biases.
    More info at https://docs.wandb.ai/guides/integrations/lightning.
    """
    def __init__(self, offline: bool = False) -> None:
        super().__init__()
        self.offline = offline
        self.type = 'WandbLogger'

    def setup(self, experiment, gl_lightning_module) -> None:
        run_directory = self.get_run_directory(experiment)
        self.create_directory(run_directory)
        self.logger = WandbLogger(save_dir=run_directory,
                                    config=self.create_config(experiment),
                                    **self.create_parameters(experiment))
        if LogModelParameters in experiment.training_callbacks:
            self.logger.watch(gl_lightning_module.net, log='all', log_freq=experiment.log_every_n_steps)
            experiment.training_callbacks().remove(LogModelParameters)

    def create_config(self, experiment) -> dict:
        return {
            "random_seed": experiment.random_seed,
            "epochs": experiment.max_epochs,
            "learning_rate": experiment.optimizer_parameters['network']['lr'], 
            "batch_size": experiment.batch_size,
        }
    
    def create_parameters(self, experiment) -> dict:
        return {
            'project': experiment.project, 
            'name': experiment.experiment_name,
            'tags': experiment.tags, 
            'notes': experiment.info, 
            'log_model': 'all',
            'offline': False,
        }


def browse_folder(data_folder, extension=None):
    """
    Browse folder given to find hdf5 files
    Parameters
    ----------
    data_folder (string)
    extension (string)

    Returns
    -------
    set of hdf5 files
    """
    logger = logging.getLogger(__name__)
    if extension is None:
        extension = ['.hdf5', '.h5']
    try:
        assert isinstance(extension, list)
    except AssertionError as e:
        logger.exception('extension must be provided as a list')
        raise e
    logger.debug('browse folder')
    file_set = set()
    for dirname, dirnames, filenames in os.walk(data_folder):
        logger.debug('found folders : {}'.format(dirnames))
        logger.debug('in {}'.format(dirname))
        logger.debug('found files : {}'.format(filenames))
        for file in filenames:
            filename, ext = os.path.splitext(file)
            if ext in extension:
                file_set.add(dirname + '/' + file)
    return file_set


def prepare_experiment_folder(main_directory, experiment_name):
    """
    Prepare experiment folder and check if already exists
    Parameters
    ----------
    main_directory (string)
    experiment_name (string)

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    experiment_directory = main_directory + '/' + experiment_name + '/'
    if not os.path.exists(experiment_directory):
        os.makedirs(experiment_directory)
        os.chmod(experiment_directory, 0o775)
    else:
        logger.info('The experiment {} already exists !'.format(experiment_name))
    logger.info('Experiment directory: %s ' % experiment_directory)


def prepare_gammaboard_folder(main_directory, experiment_name):
    """
    Prepare tensorboard run folder for the experiment
    Parameters
    ----------
    main_directory (string)
    experiment_name (string)

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    test_directory = main_directory + '/gammaboard/' + experiment_name
    if not os.path.exists(test_directory):
        os.makedirs(test_directory)
        os.chmod(test_directory, 0o775)
    logger.debug('Gammaboard runs directory: {} '.format(test_directory))
    return test_directory


def get_torch_weights_from_lightning_checkpoint(checkpoint):
    """
    Parameters
    ----------
    checkpoint

    Returns
    -------
    Torch state dict
    """
    try:
        checkpoint = torch.load(checkpoint, map_location='cpu')
        state_dict = checkpoint['state_dict']
        torch_state_dict = {}
        for k, v in state_dict.items():
            key = k[4:] if k.startswith('net.') else k
            torch_state_dict[key] = v
        return torch_state_dict
    except Exception as e:
        return None


def find_datafiles(data_folders, files_max_number=-1):
    """
    Find datafiles in the folders specified
    Parameters
    ----------
    data_folders (list): the folders where the data are stored
    train_files_max_number (int, optional): the maximum number of files to keep per folder

    Returns
    -------

    """
    logger = logging.getLogger(__name__)
    logger.debug('data folders : {}'.format(data_folders))

    # We can have several folders
    datafiles = set()

    # If the path specified in the experiment settings is not a list, turns it into a list of one element
    data_folders = [data_folders] if isinstance(data_folders, str) else data_folders

    # If files_max_number is an integer, turns it into a list of one element.
    files_max_number = [files_max_number] if isinstance(files_max_number, int) else files_max_number

    # If files_max_number is a list of multiple integers, each integer specifies the number of data to load for the
    # corresponding folder, otherwise, give the same max_number for all folders
    assert len(files_max_number) == 1 or len(files_max_number) == len(data_folders), \
        "Number of max files not matching number of folders."
    if not (len(files_max_number) == len(data_folders)):
        files_max_number *= len(data_folders)

    for folder, max_number in zip(data_folders, files_max_number):
        logger.debug('data folder : {}'.format(folder))
        dataf = list(browse_folder(folder))
        random.shuffle(dataf)
        # max_number of value -1 means load all data
        if max_number and 0 < max_number <= len(dataf):
            dataf = dataf[0:max_number]
        dataf = set(dataf)
        datafiles.update(dataf)

    return datafiles


def is_datafile_healthy(file_path):
    """
    Check that the data file does not contain empty dataset
    Parameters
    ----------
    file_path (str): the path to the file

    Returns
    -------
    A boolean
    """
    dataset_emptiness = []

    _, ext = os.path.splitext(file_path)
    if ext in ['.hdf5', '.h5']:
        with tables.File(file_path, 'r') as f:
            for n in f.walk_nodes():
                if isinstance(n, tables.Table):
                    dataset_emptiness.append(n.shape[0])
    return not np.any(np.array(dataset_emptiness) == 0)


def compute_total_parameter_number(net):
    """
    Compute the total number of parameters of a network
    Parameters
    ----------
    net (nn.Module): the network

    Returns
    -------
    int: the number of parameters
    """
    return sum(
        param.clone().cpu().data.view(-1).size(0)
        for name, param in net.named_parameters()
    )


@deprecated("20-08-2021",
            "the camera parameters are now loaded from the camera geometry, read from datafiles",
            "get_camera_layout_from_geom")
def load_camera_parameters(camera_type):
    """
    Load camera parameters : nbCol and injTable
    Parameters
    ----------
    datafiles (List) : files to load data from
    camera_type (str): the type of camera to load data for ; eg 'LST_LSTCam'

    Returns
    -------
    A dictionary
    """
    camera_parameters = {}
    if camera_type == 'LST':
        camera_type = 'LST_LSTCam'
    if camera_type in ['LST_LSTCam', 'MST_FlashCam', 'MST_NectarCam', 'CIFAR']:
        camera_parameters['layout'] = 'Hex'
    else:
        camera_parameters['layout'] = 'Square'
    camera_parameters_file = pkg_resources.resource_filename(__name__, 'data/camera_parameters.h5')
    with tables.File(camera_parameters_file, 'r') as hdf5_file:
        camera_parameters['nbRow'] = hdf5_file.root[camera_type]._v_attrs.nbRow
        camera_parameters['nbCol'] = hdf5_file.root[camera_type]._v_attrs.nbCol
        camera_parameters['injTable'] = hdf5_file.root[camera_type].injTable[()]
        camera_parameters['pixelsPosition'] = hdf5_file.root[camera_type].pixelsPosition[()]

    return camera_parameters


def fetch_data_module_settings(experiment, train, domain):
    """
    Load the data module described in the experiment setting file.
    Parameters
    ----------
    experiment: the experiment instance
    train: True or False depending on the train/test context
    domain: 'source' or 'target' if domain adaptation or None if no domain adaptation

    Returns
    -------
    The data module.
    """
    if domain is None:  # No domain adaptation
        return experiment.data_module_train if train else experiment.data_module_test
    else:  # Domain adaptation
        return experiment.data_module_train[domain] if train else experiment.data_module_test


def dump_config_filters(exp_settings, experiment, train, domain):
    data_module = fetch_data_module_settings(experiment, train=train, domain=domain)
    domain = '' if domain is None else domain

    # If test context, store the test folder path.
    if train is False:
        if data_module['paths']:
            exp_settings['test_folders'] = data_module['paths']

    exp_settings['files_folders ' + domain] = data_module['paths']
    if data_module['image_filter']:
        image_filter = data_module['image_filter']
        exp_settings['image filters ' + domain] = {format_name(filter_func): filter_param
                                                   for filter_func, filter_param
                                                   in image_filter.items()}
    if data_module['event_filter']:
        event_filter = data_module['event_filter']
        exp_settings['event filters ' + domain] = {format_name(filter_func): filter_param
                                                   for filter_func, filter_param
                                                   in event_filter.items()}

    return exp_settings


def dump_experiment_config(experiment):
    """
    Load experiment info from the settings file
    Parameters
    ----------
    experiment (Experiment): experiment

    Returns
    -------

    """
    exp_settings = collections.OrderedDict({'exp_name': experiment.experiment_name,
                                            'gammalearn': version.__version__,
                                            'dataset_class': format_name(experiment.dataset_class),
                                            'dataset_parameters': experiment.dataset_parameters,
                                            })
    exp_settings['network'] = {
        format_name(experiment.net_parameters_dic['model']): {k: format_name(v)
                                                              for k, v in
                                                              experiment.net_parameters_dic['parameters'].items()}}
    if experiment.checkpoint_path is not None:
        exp_settings['resume_checkpoint'] = os.path.join(os.path.dirname(experiment.checkpoint_path).split('/')[-1],
                                                         os.path.basename(experiment.checkpoint_path))
    if experiment.info is not None:
        exp_settings['info'] = experiment.info

    if experiment.train:
        exp_settings['num_epochs'] = experiment.max_epochs
        exp_settings['batch_size'] = experiment.batch_size

        if experiment.context['train'] == 'domain_adaptation':
            for domain in ['source', 'target']:
                exp_settings = dump_config_filters(exp_settings, experiment, train=True, domain=domain)
        else:
            exp_settings = dump_config_filters(exp_settings, experiment, train=True, domain=None)

        for k, v in experiment.targets.items():
            loss = format_name(v.get('loss', None))
            weight = v.get('loss_weight', None)
            if weight is not None:
                weight = None if isinstance(weight, BaseW) else weight

            exp_settings['losses'] = {
                k: {
                    'loss': loss,
                    'weight': weight
                }
            }

        exp_settings['loss_function'] = format_name(experiment.loss_balancing)
        exp_settings['optimizer'] = {key: format_name(value) for key, value in experiment.optimizer_dic.items()}
        exp_settings['optimizer_parameters'] = {opt: {key: format_name(value)
                                                      for key, value in param.items()}
                                                for opt, param in experiment.optimizer_parameters.items()}
        if experiment.lr_schedulers is not None:
            exp_settings['lr_schedulers'] = {
                net_param: {format_name(scheduler): param for scheduler, param in scheduler_param.items()}
                for net_param, scheduler_param in experiment.lr_schedulers.items()}

    if experiment.test:
        if experiment.data_module_test is not None:
            exp_settings = dump_config_filters(exp_settings, experiment, train=False, domain=None)

    experiment_path = experiment.main_directory + '/' + experiment.experiment_name + '/'
    settings_path = experiment_path + experiment.experiment_name + '_settings.json'
    with open(settings_path, 'w') as f:
        json.dump(exp_settings, f)


def format_name(name):
    name = format(name)
    name = name.replace('<', '').replace('>', '').replace('class ', '').replace("'", "").replace('function ', '')
    return name.split(' at ')[0]


def check_particle_mapping(particle_dict):
    assert len(particle_dict) == len(set(particle_dict.values())), 'Each mc particle type must have its own class'


def merge_list_of_dict(list_of_dict):
    merge_dict = {}
    for dictionary in list_of_dict:
        for k, v in dictionary.items():
            if k not in merge_dict:
                merge_dict[k] = [v]
            else:
                merge_dict[k].append(v)
    return merge_dict


def prepare_dict_of_tensors(dic):
    new_dic = {}
    for k, v in dic.items():
        while v.ndim > 2:
            v.squeeze_(0).squeeze_(-1)
        if v.ndim == 2:
            v.squeeze_(-1)
        new_dic[k] = v.view(-1, v.shape[-1]).tolist() if v.ndim > 1 else v.tolist()
    return new_dic


# TODO Remove when corresponding lstchain function is exposed
def write_dataframe(dataframe, outfile, table_path, mode="a", index=False, complib='blosc:zstd', complevel=1):
    """
    Write a pandas dataframe to a HDF5 file using pytables formatting.
    Re-implementation of https://github.com/cta-observatory/cta-lstchain/blob/1280e47950726f92200e1624ca38c672760e9d77/lstchain/io/io.py#L771
    to allow for compression
    
    Parameters
    ----------
    dataframe: `pandas.DataFrame`
    outfile: path
    table_path: str
        path to the table to write in the HDF5 file
    mode: str
        'a' to append to an existing file, 'w' to overwrite
    index: bool
        whether to write the index of the dataframe
    complib: str
        compression library to use
    complevel: int
        compression level to use

    Returns
    -------
    None

    """
    filters = tables.Filters(complevel=complevel, complib=complib)

    if not table_path.startswith("/"):
        table_path = "/" + table_path

    with tables.open_file(outfile, mode=mode) as f:
        path, table_name = table_path.rsplit("/", maxsplit=1)

        f.create_table(
            path,
            table_name,
            dataframe.to_records(index=index),
            createparents=True,
            filters=filters
        )


###########
# Filters #
###########
##################################################################################################
# Event base filters

def energyband_filter(dataset, energy=None, filter_only_gammas=False):
    """
    Filter dataset on energy (in TeV).
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    energy (float): energy in TeV
    filter_only_gammas (bool)

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if dataset.simu:
        if energy is None:
            energy = [0, np.inf]
        en_min = energy[0]
        en_max = energy[1]
        energy_mask = (dataset.dl1_params['mc_energy'] > en_min) & (dataset.dl1_params['mc_energy'] < en_max)
        if filter_only_gammas:
            energy_mask = energy_mask | (dataset.dl1_params['mc_type'] != GAMMA_ID)
    else:
        energy_mask = np.full(len(dataset.dl1_params), True)
    return energy_mask


def telescope_multiplicity_filter(dataset, multiplicity, strict=False):
    """
    Filter dataset on number of telescopes that triggered (for a particular type of telescope)
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    multiplicity (int): the number of telescopes that triggered
    strict (bool)

    Returns
    -------
    (list of bool): the mask to filter the data
    """

    event_ids, mult = np.unique(dataset.dl1_params['event_id'], return_counts=True)
    event_id_mask = mult == multiplicity if strict else mult >= multiplicity

    return np.in1d(dataset.dl1_params['event_id'], event_ids[event_id_mask])


def emission_cone_filter(dataset, max_angle=np.inf):
    """
    Filter the dataset on the maximum distance between the impact point and the telescope position in km
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    max_angle (float): the max angle between the telescope pointing direction and the direction of the shower in rad

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if dataset.simu:
        separations = angular_separation_altaz(dataset.dl1_params['mc_alt'], dataset.dl1_params['mc_az'],
                                               dataset.dl1_params['mc_alt_tel'], dataset.dl1_params['mc_az_tel'])
        mask = separations <= max_angle
    else:
        mask = np.full(len(dataset.dl1_params), True)
    return mask


def impact_distance_filter(dataset, max_distance=np.inf):
    """
    Filter the dataset on the maximum distance between the impact point and the telescope position in km
    Parameters
    ----------
    dataset (Dataset): the dataset to filter
    max_distance (float): the maximum distance between the impact point and the telescope position in km

    Returns
    -------
    (list of bool): the mask to filter the data
        """
    if dataset.simu:
        distances = np.sqrt((dataset.dl1_params['mc_core_x'] - dataset.dl1_params['tel_pos_x']) ** 2 +
                            (dataset.dl1_params['mc_core_y'] - dataset.dl1_params['tel_pos_y']) ** 2)
        mask = distances < max_distance
    else:
        mask = np.full(len(dataset.dl1_params), True)
    return mask


##################################################################################################
# Image base filters

def intensity_filter(dataset, intensity=None, cleaning=False, dl1=False, **opts):
    """
    Filter dataset on intensity (in pe)
    Parameters
    ----------
    dataset (Dataset) : the dataset to filter
    a (int): total intensity in photoelectrons
    cleaning (bool): cut after cleaning
    dl1 (bool): whether to use the info computed by lstchain or to recompute the value
    opts (dict): cleaning options

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if intensity is None:
        intensity = [-np.inf, np.inf]
    pe_min = intensity[0]
    pe_max = intensity[1]

    if dl1:
        return (pe_min < dataset.dl1_params['intensity']) & (dataset.dl1_params['intensity'] < pe_max)
    else:

        def clean(img):
            mask = tailcuts_clean(geom, img, **opts)
            return img * mask

        if cleaning:
            geom = dataset.original_geometry
            image_cleaned = np.apply_along_axis(clean, 1, dataset.images)
            amps = image_cleaned.sum(axis=-1)
        else:
            amps = dataset.images.sum(axis=-1)
        mask1 = pe_min < amps
        mask2 = amps < pe_max
        mask = mask1 & mask2
        return mask


def cleaning_filter(dataset, dl1=False, **opts):
    """
    Filter images according to a cleaning operation.

    Parameters
    ----------
    dataset: `Dataset`
    dl1: (bool) whether to use the info computed by lstchain or to recompute the value

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    if dl1:
        return dataset.dl1_params['n_pixels'] > 0
    else:
        geom = dataset.original_geometry

        def clean(img):
            return tailcuts_clean(geom, img, **opts)

        clean_mask = np.apply_along_axis(clean, 1, dataset.images)
        mask = clean_mask.any(axis=1)

        return mask


def leakage_filter(dataset, leakage1_cut=None, leakage2_cut=None, dl1=False, **opts):
    """
    Filter images according to a cleaning operation.

    Parameters
    ----------
    dataset: `Dataset`
    leakage1_cut: `int`
    leakage2_cut: `int`
    dl1: `bool` whether to use the info computed by lstchain or to recompute the value

    Returns
    -------
    (list of bool): the mask to filter the data
    """
    assert leakage1_cut is not None or leakage2_cut is not None, 'Leakage filter: At least one cut must be defined'
    if dl1:
        if leakage1_cut is not None:
            img_mask1 = dataset.dl1_params['leakage_intensity_width_1'] < leakage1_cut
        else:
            img_mask1 = np.full(len(dataset.dl1_params), True)

        if leakage2_cut is not None:
            img_mask2 = dataset.dl1_params['leakage_intensity_width_2'] < leakage2_cut
        else:
            img_mask2 = np.full(len(dataset.dl1_params), True)

        img_mask = img_mask1 & img_mask2

        return img_mask
    else:
        geom = dataset.original_geometry

        def leak2(img):
            mask = tailcuts_clean(geom, img, **opts)
            if np.any(mask):
                return leakage_parameters(geom, img, mask).intensity_width_2
            else:
                return 1.

        def leak1(img):
            mask = tailcuts_clean(geom, img, **opts)
            if np.any(mask):
                return leakage_parameters(geom, img, mask).intensity_width_1
            else:
                return 1.

        if leakage1_cut is not None:
            image_leak1 = np.apply_along_axis(leak1, 1, dataset.images)
            img_mask1 = image_leak1 < leakage1_cut
        else:
            img_mask1 = np.full(dataset.images.shape[0], True)

        if leakage2_cut is not None:
            image_leak2 = np.apply_along_axis(leak2, 1, dataset.images)
            img_mask2 = image_leak2 < leakage2_cut
        else:
            img_mask2 = np.full(dataset.images.shape[0], True)

        img_mask = img_mask1 & img_mask2

        return img_mask


def shower_position_filter(dataset, max_distance, dl1=False, **opts):
    """Filter images according to the position of the centroid of the shower.
    The image is cleaned then Hillas parameters are computed. For the LST a distance of 0.5 m corresponds to 10 pixels.

    Parameters
    ----------
    dataset (`Dataset`)
    max_distance (float): distance to the center of the camera in meters
    opts (dict): cleaning options
    dl1 (bool): whether to use the info computed by lstchain or to recompute the value

    Returns
    -------
    (list of bool): the mask to filter the data

    """
    if dl1:
        shower_distance = dataset.dl1_params['x'] ** 2 + dataset.dl1_params['y'] ** 2
        return shower_distance < max_distance ** 2
    else:
        geom = dataset.original_geometry

        def shower_centroid(img):
            mask = tailcuts_clean(geom, img, **opts)
            if np.any(mask):
                hillas = hillas_parameters(geom[mask], img[mask])
                return hillas.x.value ** 2 + hillas.y.value ** 2
            else:
                return np.inf

        shower_distance = np.apply_along_axis(shower_centroid, 1, dataset.images)
        img_mask = shower_distance < max_distance ** 2

        return img_mask


###################
# Transformations #
###################

def rotated_indices(pixels_position, theta):
    """
    Function that returns the rotated indices of an image from the pixels position.

    Parameters
    ----------
    pixels_position (numpy.Array): an array of shape (n, 2) of the position of the pixels
    theta (float): angle of rotation

    Returns
    -------
    Rotated indices
    """
    from math import isclose
    rot_indices = np.zeros(len(pixels_position)).astype(int)
    rotation_matrix = [[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]]
    new_pix_pos = np.matmul(rotation_matrix, pixels_position.T).T.astype(np.float32)

    for i, pos in enumerate(new_pix_pos):
        for j, old_pos in enumerate(pixels_position):
            if isclose(old_pos[0], pos[0], abs_tol=10e-5) and isclose(old_pos[1], pos[1], abs_tol=10e-5):
                rot_indices[j] = i
    assert len(set(list(rot_indices))) == len(pixels_position), \
        'Rotated indices do not match the length of pixels position.'

    return rot_indices


# TODO move to transforms
def center_time(dataset, **opts):
    """
    Center pixel time based on the max intensity pixel

    Parameters
    ----------
    dataset: `Dataset`

    Returns
    -------
    indices: `numpy.array`
    """
    geom = dataset.camera_geometry

    def clean(img):
        return tailcuts_clean(geom, img, **opts)

    clean_mask = np.apply_along_axis(clean, 1, dataset.images)

    cleaned = dataset.images * clean_mask
    max_pix = cleaned.argmax(axis=1)
    for i, times in enumerate(dataset.times):
        times -= times[max_pix[i]]


# TODO move to transforms
def rgb_to_grays(dataset):
    """
    Function to convert RGB images to 2 channels gray images.
    Parameters
    ----------
    dataset (Dataset)
    """
    assert dataset.images.ndim in [3, 4]
    assert dataset.images.shape[1] == 3
    d_size = dataset.images.shape
    gamma = 2.2
    new_images = np.empty((d_size[0], 2) + d_size[2:], dtype=np.float32)
    new_images[:, 0:1] = np.sum(dataset.images, 1, keepdims=True)  # Naive sum
    new_images[:, 1:] = (0.2126 * dataset.images[:, 0:1] ** gamma
                         + 0.7152 * dataset.images[:, 1:2] ** gamma
                         + 0.0722 * dataset.images[:, 2:] ** gamma)  # weighted sum

    dataset.images = new_images

    return np.arange(len(dataset))


def get_index_matrix_from_geom(camera_geometry):
    """
    Compute the index matrix from a ctapipe CameraGeometry

    Parameters
    ----------
    camera_geometry: `ctapipe.instrument.CameraGeometry`

    Returns
    -------
    indices_matrix: `numpy.ndarray`
        shape (n, n)

    """
    from ctapipe.image import geometry_converter_hex

    # the converter needs an image, let's create a fake one
    image = np.zeros(camera_geometry.n_pixels)

    # make sure the conversion matrix is recomputed
    if camera_geometry.camera_name in geometry_converter_hex.rot_buffer:
        del geometry_converter_hex.rot_buffer[camera_geometry.camera_name]

    geometry_converter_hex.convert_geometry_hex1d_to_rect2d(camera_geometry,
                                                            image,
                                                            key=camera_geometry.camera_name)

    hex_to_rect_map = geometry_converter_hex.rot_buffer[camera_geometry.camera_name][2]

    return np.flip(hex_to_rect_map, axis=0).astype(np.float32)


def get_camera_layout_from_geom(camera_geometry):
    """
    From a ctapipe camera geometry, compute the index matrix and the camera layout (`Hex` or `Square`) for indexed conv

    Parameters
    ----------
    camera_geometry: `ctapipe.instrument.CameraGeometry`

    Returns
    -------
    tensor_matrix: `torch.Tensor`
        shape (1, 1, n, n)
    camera_layout: `str`
        `Hex` or `Square`

    """
    index_matrix = get_index_matrix_from_geom(camera_geometry)
    tensor_matrix = torch.tensor(np.ascontiguousarray(index_matrix.reshape(1, 1, *index_matrix.shape)))
    if camera_geometry.pix_type.value == 'hexagon':
        camera_layout = 'Hex'
    elif camera_geometry.pix_type.value == 'square':
        camera_layout = 'Square'
    else:
        raise ValueError("Unkown camera pixels type")
    return tensor_matrix, camera_layout


def get_dataset_geom(d, geometries):
    """
    Update `geometries` by append the geometries from d

    Parameters
    ----------
    d: list or `torch.utils.ConcatDataset` or `torch.utils.data.Subset` or `torch.utils.data.Dataset`
    geometries: list

    """
    if isinstance(d, list):
        for d_l in d:
            get_dataset_geom(d_l, geometries)
    else:
        geometries.append(gammalearn.datasets.fetch_dataset_geometry(d))


def inject_geometry_into_parameters(parameters: dict, camera_geometry):
    """
    Adds camera geometry in model backbone parameters
    """
    for k, v in parameters.items():
        if k == 'backbone':
            v['parameters']['camera_geometry'] = camera_geometry
        elif isinstance(v, dict):
            parameters[k] = inject_geometry_into_parameters(v, camera_geometry)
    return parameters


def nets_definition_path():
    """
    Return the path to the net definition file

    Returns
    -------
    str
    """
    return pkg_resources.resource_filename('gammalearn', 'data/nets.py')


def compute_dann_hparams(module, gamma=10):
    if module.experiment.targets['domain_class']['mt_balancing']:
        lambda_p = module.experiment.loss_balancing.precisions['domain_class'].item()
    elif not module.experiment.targets['domain_class'].get('lambda_p', True):
        lambda_p = module.experiment.targets['domain_class']['loss_weight']
    else:
        current_step = module.trainer.fit_loop.total_batch_idx + 1
        max_steps = module.trainer.estimated_stepping_batches
        p = torch.tensor(current_step / max_steps, dtype=torch.float32)  # Training progress (from 0 to 1)
        lambda_p = 2.0 / (1.0 + torch.exp(-gamma * p)) - 1.0

    return lambda_p


class BaseW:
    """
    This class is inspired from the Pytorch LRScheduler that defines a learning rate scheduler. Analogically, the
    purpose of this class is to introduce a time-dependent loss weight.
    The module parameter is set within the 'gammalearn.experiment_runner.Experiment' class and provides the current and
    the max step information from the Pytorch Lightning Trainer that is involved in the training.
    Parameters
    ----------
    apply_on_grads (bool): Whether the weight must be applied on the gradients (e.g. for DANN).
    Returns
    -------
    lambda_p (float): the step-dependent loss weight
    """
    def __init__(self, apply_on_grads=False):
        self.apply_on_grads = apply_on_grads

    def function(self, p):
        return NotImplementedError

    def get_weight(self, trainer):
        if trainer is None:
            return 1.
        else:
            current_step = trainer.fit_loop.total_batch_idx + 1
            max_step = trainer.estimated_stepping_batches
            p = torch.tensor(current_step / max_step, dtype=torch.float32)  # Training progress (from 0 to 1)
            return self.function(p)


class ExponentialW(BaseW):
    """
    Compute the exponential weight corresponding to the domain adaptation loss weight proposed in Domain-Adversarial
    Training of Neural Networks (DANN) (https://doi.org/10.48550/arxiv.1505.07818) from Y. Ganin.
    This class is particularly useful when applied to the DANN 'loss_weight' argument but may also be applied in other
    context. In more details, in the experiment setting file and in the case of DANN, this class can be used as follows:
    targets = collections.OrderedDict({
        'domain_class': {
            ...,
            'loss_weight': ExponentialW(gamma=10),
            ...,
        }
    })
    Parameters
    ----------
    gamma (int): the exponential coefficient exp(-gamma*p).
    """

    def __init__(self, apply_on_grads, gamma=10):
        super().__init__(apply_on_grads)
        self.gamma = torch.tensor(gamma, dtype=torch.float32)

    def function(self, p):
        return 2.0 / (1.0 + torch.exp(-self.gamma * p)) - 1.0
    

class DistributionW:
    """

    Parameters
    ----------
    path (str): the path to the csv file containing the distribution
    """

    def __init__(self, path: str) -> None:
        assert os.path.exists(path)
        self.distrib = pd.read_csv(path)

    def apply(self, loss: torch.Tensor, entry: torch.Tensor) -> torch.Tensor:
        loss_weighted = loss.clone()
        xp = self.distrib['x'].to_numpy()
        fp = self.distrib['y'].to_numpy()
        x = entry.cpu().numpy()
        fx = torch.from_numpy(np.interp(x, xp, fp))
        weights = fx.to(loss.device)
        loss_weighted = loss_weighted * weights

        return loss_weighted


# Transformer utility functions
def get_centroids_from_patches(patches, geom):
    """
    Compute module centroid positions from patch indices and geometry
    Parameters
    ----------
    patches (torch.Tensor): pixel indices for each patch, corresponding to pixel modules
    geom (ctapipe.CameraGeometry): geometry
    Returns
    -------
    torch.Tensor
    """
    x = geom.pix_x.value.astype(np.float32)
    y = geom.pix_y.value.astype(np.float32)
    centroids = []
    for mod in patches:
        pix_x = x[mod.numpy()]
        pix_y = y[mod.numpy()]
        centroid_x = np.mean(pix_x)
        centroid_y = np.mean(pix_y)
        centroids.append([centroid_x, centroid_y])
    return torch.from_numpy(np.array(centroids))


def check_patches(patch_indices, patch_centroids, geom, width_ratio=1.2):
    """
    Check patch indices validity
    Parameters
    ----------
    patch_indices (torch.Tensor): pixel indices for each patch, corresponding to pixel modules
    patch_centroids (torch.Tensor): position of the module centroids
    geom (ctapipe.CameraGeometry): geometry
    width_ratio (int): tolerance to check pixel distance to centroid
    Returns
    -------
    """
    x = geom.pix_x.value.astype(np.float32)
    y = geom.pix_y.value.astype(np.float32)
    radius = (geom.pixel_width[0].value.astype(np.float32) * width_ratio) ** 2
    distance_from_centroid = []
    # We check that each pixel in a module lies in a circle
    # of diameter pixel width * width_ratio around the module centroid
    for mod, centroid in zip(patch_indices, patch_centroids):
        pix_x = x[mod.numpy()]
        pix_y = y[mod.numpy()]
        centroid_x = centroid[0].numpy()
        centroid_y = centroid[1].numpy()
        distance_from_centroid.append((pix_x - centroid_x) ** 2 + (pix_y - centroid_y) ** 2)
    distance_from_centroid = np.concatenate(distance_from_centroid, axis=0)
    assert (distance_from_centroid < radius).all(), '{} - {}'.format(distance_from_centroid, radius)


def get_patch_indices_and_centroids_from_geometry(geom):
    """
    Compute patch indices and centroid positions from geometry
    Parameters
    ----------
    geom (ctapipe.CameraGeometry): geometry
    Returns
    -------
    (torch.Tensor, torch.Tensor)
    """
    try:
        # Try with LSTCam geometry
        pixel_ids = torch.arange(geom.n_pixels)
        patch_indices = pixel_ids.view(-1, 7)
        patch_centroids = get_centroids_from_patches(patch_indices, geom)
        check_patches(patch_indices, patch_centroids, geom, width_ratio=1.2)
    except AssertionError:
        # Try with geometry from files (lstchain_0.7)
        try:
            module_per_pixel_file = pkg_resources.resource_filename('gammalearn',
                                                                    'data/module_id_per_pixel_lstchain_0.7.txt')
            pixel_module_df = pd.read_csv(module_per_pixel_file, sep=' ')
            patch_indices = []
            for mod in set(pixel_module_df['mod_id']):
                patch_indices.append(pixel_module_df['pix_id'][pixel_module_df['mod_id'] == mod].values)
            patch_indices = torch.tensor(np.stack(patch_indices, axis=0))
            patch_centroids = get_centroids_from_patches(patch_indices, geom)
            check_patches(patch_indices, patch_centroids, geom, width_ratio=1.2)
        except AssertionError as e:
            logging.warning('Unable to retrieve pixel modules from geometry')
            raise e
        else:
            return patch_indices, patch_centroids
    else:
        return patch_indices, patch_centroids


def get_2d_sincos_pos_embedding_from_patch_centroids(centroids, embed_dim, additional_tokens=None, add_pointing=False):
    """
    Compute 2d sincos positional embedding from pixel module centroid positions
    Parameters
    ----------
    centroids (torch.Tensor): x and y position of pixel module centroids
    embed_dim (int): dimension of embedding
    additional_tokens (list): list of additional tokens for which add an embedding
    Returns
    -------
    torch.Tensor
    """
    # Rescale centroids to get closer to classical 2d image grid
    y_width = np.ptp(centroids[:, 1])
    ratio = np.sqrt(len(centroids)) / y_width
    centroids[:, 0] -= centroids[:, 0].min()
    centroids[:, 1] -= centroids[:, 1].min()
    centroids *= ratio

    pos_embed = calculate_pos_emb(embed_dim, centroids)

    return add_tokens_to_pos_embed(pos_embed, additional_tokens, add_pointing, embed_dim)


def get_patch_indices_and_grid(image_size, patch_size):
    image_height, image_width = image_size['height'], image_size['width']
    check_grid(image_height, image_width, patch_size)

    n_patches_h, n_patches_w = (image_height // patch_size), (image_width // patch_size)
    n_patches = n_patches_h * n_patches_w

    # Compute patch indices
    pixel_ids = torch.arange(image_height * image_width)
    pixel_ids = pixel_ids.view(-1, image_width)
    patch_indices = pixel_ids.unfold(0, patch_size, patch_size).unfold(1, patch_size, patch_size)
    patch_indices = patch_indices.flatten(start_dim=2)
    patch_indices = patch_indices.view(n_patches, -1)

    # Compute patch grid
    grid_h = torch.arange(n_patches_h)
    grid_w = torch.arange(n_patches_w)
    grid = torch.meshgrid(grid_w, grid_h, indexing='ij')
    grid = torch.stack(grid, dim=0)
    grid = grid.reshape(2, -1).T
    grid = grid.to(torch.float)

    return patch_indices, grid


def check_grid(image_height, image_width, patch_size):
    logger = logging.getLogger(__name__)

    try:
        assert image_height % patch_size == 0 or image_width % patch_size == 0
    except AssertionError as err:
        message = 'The patch size ({patch_s}) must divide the image height ({img_h}) and width ({img_w}).'.format(
            patch_s=patch_size, img_h=image_height, img_w=image_width)
        logger.exception(message)
        raise err


def get_2d_sincos_pos_embedding_from_grid(grid, embed_dim, additional_tokens=None, add_pointing=False):
    pos_embed = calculate_pos_emb(embed_dim, grid)

    return add_tokens_to_pos_embed(pos_embed, additional_tokens, add_pointing, embed_dim)


def calculate_pos_emb(embed_dim, positions):
    omega = torch.arange(embed_dim // 4) / (embed_dim / 4.)
    omega = 1. / 10000 ** omega
    sin_x = torch.sin(torch.mm(positions[:, 0].unsqueeze(1), omega.unsqueeze(0)))
    cos_x = torch.cos(torch.mm(positions[:, 0].unsqueeze(1), omega.unsqueeze(0)))
    sin_y = torch.sin(torch.mm(positions[:, 1].unsqueeze(1), omega.unsqueeze(0)))
    cos_y = torch.cos(torch.mm(positions[:, 1].unsqueeze(1), omega.unsqueeze(0)))
    pos_embed = torch.cat([sin_x, cos_x, sin_y, cos_y], dim=1)

    return pos_embed


def add_tokens_to_pos_embed(pos_embed, additional_tokens, add_pointing, embed_dim):
    additional_tokens = [] if additional_tokens is None else additional_tokens
    add_tokens = additional_tokens + ['pointing'] if add_pointing else additional_tokens

    if add_tokens is not None:
        try:
            assert isinstance(add_tokens, list), 'Please provide additional tokens as a list'
            for i in reversed(range(len(add_tokens))):
                pos_embed = torch.cat([torch.full((1, embed_dim), i), pos_embed], dim=0)
        except:
            logging.warning('Additional tokens not used')

    return pos_embed


def post_process_data(merged_outputs, merged_dl1_params, dataset_parameters):
    """
    Post process data produced by the inference of a model on dl1 data to make them dl2 ready
    Parameters:
    -----------
    merged_outputs (pd.Dataframe): merged outputs produced by the model at test time
    merged_dl1_params (pd.Dataframe): corresponding merged dl1 parameters
    dataset_parameters (dict): parameters used to instantiate dataset objects
    Returns:
    --------
    dl2_params
    """
    particle_dict = dataset_parameters['particle_dict']
    swapped_particle_dict = {v: k for k, v in particle_dict.items()}
    # Prepare data
    for param_name in ['mc_core_x', 'mc_core_y', 'tel_pos_x', 'tel_pos_y', 'tel_pos_z', 'mc_x_max']:
        if param_name in merged_dl1_params.columns:
            merged_dl1_params[param_name] *= 1000

    dl2_params = merged_dl1_params.copy(deep=True)

    for target in merged_outputs.columns:
        if target == 'energy':
            dl2_params['reco_energy'] = 10 ** merged_outputs[target]
        if target == 'xmax':
            dl2_params['reco_x_max'] = merged_outputs[target] * 1000
        if target == 'impact':
            dl2_params[['reco_core_x', 'reco_core_y']] = pd.DataFrame(merged_outputs[target].tolist(),
                                                                      index=dl2_params.index)
            dl2_params['reco_core_x'] *= 1000
            dl2_params['reco_core_y'] *= 1000
            if dataset_parameters['group_by'] == 'image':
                dl2_params['reco_core_x'] += dl2_params['tel_pos_x']
                dl2_params['reco_core_y'] += dl2_params['tel_pos_y']
        if target == 'direction':
            dl2_params[['reco_alt', 'reco_az']] = pd.DataFrame(merged_outputs[target].tolist(),
                                                               index=dl2_params.index)
            if dataset_parameters['group_by'] == 'image':
                alt_tel = dl2_params['mc_alt_tel'] if 'mc_alt_tel' in dl2_params.columns else dl2_params['alt_tel']
                az_tel = dl2_params['mc_az_tel'] if 'mc_az_tel' in dl2_params.columns else dl2_params['az_tel']
                dl2_params['reco_alt'] += alt_tel
                dl2_params['reco_az'] += az_tel
        if target == 'class':
            probabilities = torch.nn.functional.softmax(torch.tensor(list(merged_outputs[target].values)), dim=1)
            dl2_params['reco_particle'] = np.vectorize(swapped_particle_dict.get)(np.argmax(probabilities, 1))
            dl2_params['gammaness'] = probabilities[:, particle_dict[GAMMA_ID]]
            for k, v in particle_dict.items():
                dl2_params['reco_proba_{}'.format(k)] = probabilities[:, v]

    return dl2_params


def write_dl2_file(dl2_params, dl1_dataset, output_path, mc_type=None, mc_energies=None):
    """
    Writes dl2 file from reconstructed dl2 params and dl1 dataset
    """
    metadata = dl1_dataset.run_config['metadata']
    if mc_type is not None:
        metadata['mc_type'] = mc_type
    metadata['GAMMALEARN_VERSION'] = gl_version.__version__
    # Copy dl1 info except images
    with tables.open_file(dl1_dataset.hdf5_file_path) as dl1:
        for node in dl1.walk_nodes():
            if not isinstance(node, tables.group.Group) and 'image' not in node._v_pathname:
                stats = {'groups': 0, 'leaves': 0, 'links': 0, 'bytes': 0, 'hardlinks': 0}
                copy_leaf(
                    dl1_dataset.hdf5_file_path, output_path, node._v_pathname, node._v_pathname,
                    title='', filters=None,
                    copyuserattrs=True,
                    overwritefile=False, overwrtnodes=True,
                    stats=stats, start=None, stop=None, step=1,
                    chunkshape='keep',
                    sortby=None, check_CSI=False,
                    propindexes=False,
                    upgradeflavors=False,
                    allow_padding=True,
                )
    # Write dl2 info
    if not dl1_dataset.simu:
        # Post dl2 ops for real data
        dl2_params = add_delta_t_key(dl2_params)
    write_dl2_dataframe(dl2_params, output_path)
    # Write metadata
    if mc_energies is not None:
        pd.DataFrame({'mc_trig_energies': np.array(mc_energies)}).to_hdf(output_path, key='triggered_events')
    with tables.open_file(output_path, mode='a') as file:
        for k, item in metadata.items():
            if k in file.root._v_attrs and type(file.root._v_attrs) is list:
                attribute = file.root._v_attrs[k].extend(metadata[k])
                file.root._v_attrs[k] = attribute
            else:
                file.root._v_attrs[k] = metadata[k]


def write_dl2_dataframe(dl2_params, output_path):
    """
    Writes dl2 dataframe to hdf5 file.
    lstchain function should be used instead of this one, 
    when compression is included there (probably v>=0.11).
    
    Parameters
    ----------
    dl2_params: `pandas.DataFrame`
    output_path: `str`
    """
    write_dataframe(dl2_params, output_path, table_path=dl2_params_lstcam_key)

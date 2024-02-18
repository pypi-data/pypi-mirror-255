import collections
import os
import importlib
from pathlib import Path
import math
import numpy as np
import torch
from torch.optim import lr_scheduler
from torchvision import transforms

from torchmetrics.classification import Accuracy, AUROC
from torchmetrics.regression import MeanSquaredError
from pytorch_lightning.profiler import SimpleProfiler, AdvancedProfiler, PyTorchProfiler
from torchmetrics import JaccardIndex

import gammalearn.criterions as criterions
import gammalearn.optimizers as optimizers
import gammalearn.steps as steps
from gammalearn.callbacks import (LogGradientNorm, LogModelWeightNorm, LogModelParameters,
                                  LogUncertaintyLogVars, LogUncertaintyPrecisions, LogGradNormWeights,
                                  LogReLUActivations, LogLinearGradient, LogFeatures, WriteAccuracy)
import gammalearn.utils as utils
import gammalearn.datasets as dsets
from gammalearn.data_handlers import VisionDataModule
from gammalearn.constants import GAMMA_ID, PROTON_ID, ELECTRON_ID
import gammalearn.data.nets as nets


# Experiment settings
main_directory = str(Path.home()) + '/gammalearn_experiments'  # TODO change directory if needed
"""str: mandatory, where the experiments are stored"""
project = 'test_project'
"""str: optional, the name of the project."""
experiment_name = 'test_install'
"""str: mandatory, the name of the experiment. Should be different
for each experiment, except if one wants to resume an old experiment
"""
tags = ['test_tags']
"""list of str: optional, the tags of the experiment. Will be displayed in the wandb dashboard"""
info = ''
"""str: optional"""
gpus = 1
"""int or list: mandatory, the number of gpus to use. If -1, run on all GPUS, 
if None/0 run on CPU. If list, run on GPUS of list.
"""
log_every_n_steps = 1
"""int: optional, the interval in term of iterations for on screen
data printing during experiment. A small value may lead to a very large log file size.
"""
window_size = 100
"""int: optional, the interval in term of stored values for metric moving computation"""
checkpointing_options = dict(every_n_epochs=1, save_top_k=3, save_last=True)
"""dict: optional, specific options for model checkpointing.
See https://pytorch-lightning.readthedocs.io/en/stable/api/pytorch_lightning.callbacks.ModelCheckpoint.html 
for details.
"""
random_seed = 1
"""int: optional, the manual seed to make experiments more reproducible"""
monitor_device = True
"""bool: optional, whether or not monitoring the gpu utilization"""
targets = collections.OrderedDict({
    'autoencoder': {
        'loss': torch.nn.MSELoss(reduction='none'),
        'loss_weight': 1,
        'metrics': {
            'MSE': MeanSquaredError(),
        },
        'mt_balancing': True
    },
    'class': {
        'label_shape': 1,
        'output_shape': 10,
        'loss': torch.nn.CrossEntropyLoss(),
        'loss_weight': 1,
        'metrics': {
            'Accuracy_digit': Accuracy(threshold=0.5),
        },
        'mt_balancing': True
    },
})
"""dict: mandatory, defines for every objectives of the experiment
the loss function and its weight
"""

dataset_class = dsets.VisionDataset
"""Dataset: mandatory, the Dataset class to load the data. Currently 2 classes are available, MemoryLSTDataset that 
loads images in memory, and FileLSTDataset that loads images from files during training.
"""
dataset_parameters = {
    'targets': list(targets.keys()),
}
"""dict: mandatory, the parameters of the dataset."""
preprocessing_workers = 4
"""int: optional, the max number of workers to create dataset."""
dataloader_workers = 4
"""int: optional, the max number of workers for the data loaders. If 0, data are loaded from the main thread."""
mp_start_method = 'fork'
"""str: optional, the method to start new process in [fork, spawn]"""

# Net settings
# Uncomment following lines to import your network from an external file
# net_definition_file = utils.nets_definition_path()
# """str: mandatory, the file where to find the net definition to use"""
# # Load the network definitions module #
# spec = importlib.util.spec_from_file_location("nets", net_definition_file)
# nets = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(nets)

net_parameters_dic = {
    'model': nets.AutoEncoderClassifier,
    'parameters': {
        'backbone': {
            'model': nets.Encoder,
            'parameters': {
                'n_channels': 3,
                'latent_feature_size': (5, 5),
                'block_features': [8, 16, 32],
            }
        },
        'classifier': {
            'parameters': {
                'n_labels': 10,
            }
        },
        'decoder': {
            'model': nets.Decoder,
            'parameters': {
                'n_channels': 3,
                'block_features': [8, 16, 32],
            }
        },
    },
}

"""dict: mandatory, the parameters of the network. Depends on the
network chosen. Must include at least a model and a parameters field.
"""
# checkpoint_path = main_directory + '/test_install/checkpoint_epoch=0.ckpt'
"""str: optional, the path where to find the backup of the model to resume"""

profiler = None
# profiler = {'profiler': SimpleProfiler,
#             'options': dict(extended=True)
#             }
"""str: optional, the profiler to use"""
#########################################################################################
train = True
"""bool: mandatory, whether or not to train the model"""
# Data settings
data_module_train = {
    'module': VisionDataModule,
    'paths': [
        "/home/michael/Workspace/datasets/digits/mnist"
    ],  # TODO fill your folder path
    'transform': transforms.Compose([
        transforms.ToTensor(),
    ]),
    'target_transform': None,
}
"""paths->list: mandatory, the folders where to find the hdf5 data files"""
"""image_filter->dict: optional, the filter(s) to apply to the dataset at image level"""
"""event_filter->dict: optional, the filter(s) to apply to the dataset"""

validating_ratio = 0.2
"""float: mandatory, the ratio of data to create the validating set"""
split_by_file = False
"""bool: optional, whether to split data at the file level or at the data level"""
max_epochs = 1
"""int: mandatory, the maximum number of epochs for the experiment"""
batch_size = 2
"""int: mandatory, the size of the mini-batch"""

train_files_max_number = 100
"""int: optional, the max number of files to use for the dataset"""

pin_memory = True
"""bool: optional, whether or not to pin memory in dataloader"""


# Training settings
loss_options = {}
loss_balancing_options = {
    'log_var_coefficients': [0.5, 0.5],  # for uncertainty
    'penalty': 0,  # for uncertainty
}
"""dict: mandatory, defines for every objectives of the experiment
the loss function and its weight
"""
loss_balancing = criterions.UncertaintyWeighting(targets, **loss_balancing_options)
"""function: mandatory, the function to compute the loss"""
optimizer_dic = {
    'network': optimizers.load_adam,
    'loss_balancing': optimizers.load_adam
}
"""dict: mandatory, the optimizers to use for the experiment.
One may want to use several optimizers in case of GAN for example
"""
optimizer_parameters = {
    'network': {
        'lr': 1e-3,
        'weight_decay': 1e-4,
    },
    'loss_balancing': {
        'lr': 0.025,
    },
}
"""dict: mandatory, defines the parameters for every optimizers to use"""
# regularization = {'function': 'gradient_penalty',
#                   'weight': 10}
"""dict: optional, regularization to use during the training process. See in optimizers.py for 
available regularization functions. If `function` is set to 'gradient_penalty', the training step must be 
`training_step_mt_gradient_penalty`."""
experiment_hparams = {}
training_step = steps.get_training_step_mt(**experiment_hparams)
# training_step = steps.training_step_gradnorm
# training_step = steps.training_step_mt_gradient_penalty
"""function: mandatory, the function to compute the training step"""
eval_step = steps.get_eval_step_mt(**experiment_hparams)
"""function: mandatory, the function to compute the validating step"""
check_val_every_n_epoch = 1
"""int: optional, the interval in term of epoch for validating the model"""
lr_schedulers = {
    'network': {
        lr_scheduler.StepLR: {
            'gamma': 0.1,
            'step_size': 10,
        }
    },
    # 'network': {
    #     lr_scheduler.ReduceLROnPlateau: {
    #         'factor': 0.1,
    #         'patience': 30,
    #     }
    # },
    # 'network': {
    #     lr_scheduler.MultiStepLR: {
    #         'gamma': 0.1,
    #         'milestones': [10, 15, 18],
    #     }
    # },
    # 'network': {
    #     lr_scheduler.ExponentialLR: {
    #         'gamma': 0.9,
    #     }
    # },
}
"""dict: optional, defines the learning rate schedulers"""
# callbacks
training_callbacks = [
    LogGradientNorm(),
    LogModelWeightNorm(),
    LogModelParameters(),
    LogUncertaintyLogVars(),
    LogUncertaintyPrecisions(),
    # LogGradNormWeights(),
    LogReLUActivations(),
    LogLinearGradient(),
    # LogFeatures(),  # Do not use during training !! Very costly !!
]
"""dict: list of callbacks
"""
######################################################################################
# Testing settings
test = True
"""bool: mandatory, whether or not to test the model at the end of training"""
data_module_test = {
    'module': VisionDataModule,
    'paths': [
        "/home/michael/Workspace/datasets/digits/mnist"
    ],  # TODO fill your folder path
    'transform': transforms.Compose([
        transforms.ToTensor(),
    ]),
    'target_transform': None,
}
"""
dict: optional, must at least contain a non-empty 'source':{'paths:[]'}
path->list of str: optional, the folders containing the hdf5 data files for the test
image_filter->dict: optional, filter(s) to apply to the test set at image level
event_filter->dict: optional, filter(s) to apply to the test set
"""

test_step = steps.get_test_step_mt(**{'add_labels': True})
"""function: mandatory, the function to compute the validating step"""
dl2_path = ''
"""str: optional, path to store dl2 files"""
test_dataset_parameters = {
    # 'subarray': [1],
}
"""dict: optional, the parameters of the dataset specific to the test operation."""
test_files_max_number = 100
"""int: optional, the max number of files to use for the dataset"""
test_batch_size = 2
"""int: optional, the size of the mini-batch for the test"""
test_callbacks = [
    WriteAccuracy()
]
"""dict: list of callbacks"""

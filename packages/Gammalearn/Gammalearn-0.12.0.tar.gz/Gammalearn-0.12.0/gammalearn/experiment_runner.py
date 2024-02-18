#!/usr/bin/env python

from __future__ import division, print_function
import os
import argparse
import importlib.util
import inspect
import logging
import shutil
import faulthandler
import copy

import torch
import torch.backends.cudnn as cudnn

from pytorch_lightning import LightningModule
from pytorch_lightning.callbacks import ModelCheckpoint, DeviceStatsMonitor, LearningRateMonitor
from pytorch_lightning.strategies import DDPStrategy
import pytorch_lightning as pl

from gammalearn.version import __version__ as _version
from gammalearn.utils import (check_particle_mapping, compute_total_parameter_number, get_dataset_geom,
                              prepare_experiment_folder, dump_experiment_config, inject_geometry_into_parameters, 
                              TrainerLogger, TrainerTensorboardLogger)
from gammalearn.datasets import WrongGeometryError
from gammalearn.logging import LOGGING_CONFIG
from gammalearn.optimizers import DANNLR
from gammalearn.criterions import LossComputing, MultiLossBalancing
from gammalearn.data_handlers import VisionDataModule, VisionDomainAdaptationDataModule, GLearnDataModule, \
    GLearnDomainAdaptationDataModule
from gammalearn.constants import SOURCE, TARGET


faulthandler.enable()


class Experiment(object):
    """Loads the settings of the experiment from the settings object,
    check them and defines default values for not specified ones.
    """

    def __init__(self, settings):
        """
        Parameters
        ----------
        settings : the object created from the settings.py import
        """
        self._logger = logging.getLogger(__name__)
        self.hooks = {}
        self.camera_geometry = None

        ##################################################################################################
        # Experiment settings
        self._settings = settings

        # Load mandatory settings
        self._has_mandatory('main_directory', 'where the experiments are stored')
        self._is_of_type('main_directory', str)
        self.main_directory = settings.main_directory

        self._has_mandatory('experiment_name', 'the name of the experiment !')
        self._is_of_type('experiment_name', str)
        self.experiment_name = settings.experiment_name

        self.checkpointing_options = dict(dirpath=os.path.join(self.main_directory, self.experiment_name),
                                          monitor='Loss_validating', filename='checkpoint_{epoch}',
                                          every_n_epochs=1, save_top_k=-1)

        self._has_mandatory(
            'gpus', 'the gpus to use. If -1, run on all GPUS, if None/0 run on CPU. If list, run on GPUS of list.')
        assert isinstance(getattr(settings, 'gpus'), (int, list)) or getattr(settings, 'gpus') is None, \
            'CUDA device id must be int, list of int or None !'
        if not torch.cuda.is_available() and settings.gpus not in [None, 0]:
            self._logger.warning('Experiment requested to run on GPU, but GPU not available. Run on CPU')
            self.gpus = None
        elif settings.gpus == 0:
            self.gpus = None
        else:
            self.gpus = settings.gpus
        self.accelerator = 'gpu' if self.gpus not in [0, None] else 'cpu'
        self.strategy = 'ddp' if self.gpus not in [0, None] else None

        self._has_mandatory('dataset_class', 'the class to load the data')
        self.dataset_class = settings.dataset_class

        self._has_mandatory('dataset_parameters', 'the parameters of the dataset (camera type, group by option...)')
        self.dataset_parameters = settings.dataset_parameters
        if 'particle_dict' in self.dataset_parameters:
            check_particle_mapping(self.dataset_parameters['particle_dict'])

        self._has_mandatory('targets', 'the targets to reconstruct')
        self.targets = settings.targets

        # Net settings
        self._has_mandatory('net_parameters_dic', 'the parameters of the net described by a dictionary')
        assert isinstance(getattr(settings, 'net_parameters_dic'), dict), 'The net parameters must be a dict !'
        self.net_parameters_dic = settings.net_parameters_dic

        self._has_mandatory('train', 'whether to test the model after training')
        self._is_of_type('train', bool)
        self.train = settings.train

        self._has_mandatory('test', 'whether to test the model after training')
        self._is_of_type('test', bool)
        if settings.test and self.gpus is not None:
            if self.gpus > 1:
                self._logger.warning('Test is set to True and number of GPUs greater than 1, which is incompatible. \n \
                                     Test set to False. You will have to launch another job with maximum 1 GPU.')
                self.test = False
            else:
                self.test = settings.test
        else:
            self.test = settings.test

        # Optional experiments settings
        if hasattr(settings, 'project'):
            self._is_of_type('project', str)
            self.project = settings.project
        else:
            self.project = 'default'

        if hasattr(settings, 'info'):
            self._is_of_type('info', str)
            self.info = settings.info
        else:
            self.info = None

        if hasattr(settings, 'tags'):
            self._is_of_type('tags', list)
            self.tags = settings.tags
        else:
            self.tags = []

        if hasattr(settings, 'log_every_n_steps'):
            self._is_positive('log_every_n_steps')
            self.log_every_n_steps = settings.log_every_n_steps
        else:
            self.log_every_n_steps = 100

        if hasattr(settings, 'net_definition_file'):
            self.net_definition_file = settings.net_definition_file
        else:
            self.net_definition_file = None

        if hasattr(settings, 'checkpointing_options'):
            assert isinstance(settings.checkpointing_options, dict)
            self.checkpointing_options.update(settings.checkpointing_options)

        if hasattr(settings, 'random_seed'):
            self._is_of_type('random_seed', int)
            self.random_seed = settings.random_seed
        else:
            self.random_seed = None

        if hasattr(settings, 'monitor_device'):
            self._is_of_type('monitor_device', bool)
            self.monitor_device = settings.monitor_device
        else:
            self.monitor_device = False

        if hasattr(settings, 'data_transform'):
            self._is_of_type('data_transform', dict)
            self.data_transform = settings.data_transform
        else:
            self.data_transform = None

        if hasattr(settings, 'preprocessing_workers'):
            self._is_of_type('preprocessing_workers', int)
            self.preprocessing_workers = max(settings.preprocessing_workers, 0)
        else:
            self.preprocessing_workers = 0

        if hasattr(settings, 'dataloader_workers'):
            self._is_of_type('dataloader_workers', int)
            self.dataloader_workers = max(settings.dataloader_workers, 0)
        else:
            self.dataloader_workers = 0

        if hasattr(settings, 'mp_start_method'):
            self._is_of_type('mp_start_method', str)
            try:
                assert settings.mp_start_method in ['fork', 'spawn']
            except AssertionError:
                self.mp_start_method = torch.multiprocessing.get_start_method()
            else:
                self.mp_start_method = settings.mp_start_method
        else:
            self.mp_start_method = torch.multiprocessing.get_start_method()

        if hasattr(settings, 'checkpoint_path'):
            self.checkpoint_path = settings.checkpoint_path
        else:
            self.checkpoint_path = None

        self.profiler = settings.profiler if hasattr(settings, 'profiler') else None

        if hasattr(settings, 'trainer_logger'):
            self._is_of_type('trainer_logger', TrainerLogger)
            self.trainer_logger = settings.trainer_logger
        else:
            self.trainer_logger = TrainerTensorboardLogger()

        #################################################################################################
        # Train settings
        if self.train:
            # Data settings
            self._has_mandatory('data_module_train', 'the training and validating data folders')
            self.data_module_train = settings.data_module_train
            self.context = self._check_data_module(self.data_module_train)
            if self.context['train'] == 'domain_adaptation':
                if 'domain_dict' not in self.dataset_parameters:
                    self.dataset_parameters['domain_dict'] = {SOURCE: 1,
                                                              TARGET: 0
                                                              }

            self._has_mandatory('validating_ratio', 'the ratio of data for validation')
            self.validating_ratio = settings.validating_ratio

            self._has_mandatory('max_epochs', 'the maximum number of epochs')
            self.max_epochs = settings.max_epochs

            self._has_mandatory('batch_size', 'the batch size')
            self._is_positive('batch_size')
            self.batch_size = settings.batch_size

            # Training settings
            self._has_mandatory('optimizer_parameters', 'the optimizers parameters described as a dictionary')
            self.optimizer_parameters = settings.optimizer_parameters

            self._has_mandatory('optimizer_dic', 'the optimizers described as a dictionary')
            self.optimizer_dic = settings.optimizer_dic

            self._has_mandatory('training_step', 'the function for the training step')
            self._is_function('training_step', 2)
            self.training_step = settings.training_step

            self._has_mandatory('eval_step', 'the function for the evaluation step')
            self._is_function('eval_step', 2)
            self.eval_step = settings.eval_step

            # Optional settings
            if hasattr(settings, 'loss_balancing'):
                if settings.loss_balancing is not None:
                    self.loss_balancing = settings.loss_balancing
                else:
                    self.loss_balancing = lambda x, m: x
            else:
                self.loss_balancing = lambda x, m: x

            if hasattr(settings, 'dataset_size'):
                self._is_of_type('dataset_size', int)
                self.dataset_size = settings.dataset_size
            else:
                self.dataset_size = None

            if hasattr(settings, 'train_files_max_number'):
                self._is_of_type('train_files_max_number', (int, dict, list))
                self.train_files_max_number = settings.train_files_max_number
            else:
                self.train_files_max_number = None

            if hasattr(settings, 'pin_memory'):
                self._is_of_type('pin_memory', bool)
                self.pin_memory = settings.pin_memory
            else:
                self.pin_memory = False

            if hasattr(settings, 'regularization'):
                self.regularization = settings.regularization
            else:
                self.regularization = None

            if hasattr(settings, 'check_val_every_n_epoch'):
                self._is_positive('check_val_every_n_epoch')
                self.check_val_every_n_epoch = settings.check_val_every_n_epoch
            else:
                self.check_val_every_n_epoch = 1

            if hasattr(settings, 'lr_schedulers'):
                self.lr_schedulers = settings.lr_schedulers
            else:
                self.lr_schedulers = None

            if hasattr(settings, 'training_callbacks'):
                self.training_callbacks = settings.training_callbacks
            else:
                self.training_callbacks = []

        else:
            self.data_module_train = None
            self.validating_ratio = None
            self.max_epochs = 0
            self.batch_size = None
            self.loss_options = None
            self.loss_balancing = None
            self.optimizer_parameters = None
            self.optimizer_dic = None
            self.training_step = None
            self.eval_step = None
            self.dataset_size = None
            self.train_files_max_number = None
            self.pin_memory = False
            self.regularization = None
            self.check_val_every_n_epoch = 1
            self.lr_schedulers = None
            self.training_callbacks = []

        ########################################################################################################
        # Test settings
        if self.test:
            self._has_mandatory('test_step', 'the test iteration')
            self._is_function('test_step', 2)
            self.test_step = settings.test_step

            if hasattr(settings, 'merge_test_datasets'):
                self._is_of_type('merge_test_datasets', bool)
                self.merge_test_datasets = settings.merge_test_datasets
            else:
                self.merge_test_datasets = False

            if hasattr(settings, 'test_dataset_parameters'):
                self._is_of_type('test_dataset_parameters', dict)
                self.test_dataset_parameters = settings.test_dataset_parameters
            else: 
                self.test_dataset_parameters = None

            if hasattr(settings, 'data_module_test') and settings.data_module_test is not None:
                self.data_module_test = settings.data_module_test
                self._check_data_module(self.data_module_test, train=False)
            else:
                self.data_module_test = None

            if hasattr(settings, 'dl2_path'):
                self._is_of_type('dl2_path', str)
                self.dl2_path = settings.dl2_path
                if not self.dl2_path:
                    self.dl2_path = None
            else:
                self.dl2_path = None

            if hasattr(settings, 'output_dir'):
                self._is_of_type('output_dir', str)
                self.output_dir = settings.output_dir
                if not self.output_dir:
                    self.output_dir = None
            else:
                self.output_dir = None

            if hasattr(settings, 'output_file'):
                self._is_of_type('output_file', str)
                self.output_file = settings.output_file
                if not self.output_file:
                    self.output_file = None
            else:
                self.output_file = None

            if hasattr(settings, 'test_batch_size'):
                self.test_batch_size = settings.test_batch_size
            elif self.batch_size is not None:
                self.test_batch_size = self.batch_size
            else:
                raise ValueError

            if hasattr(settings, 'test_callbacks'):
                self.test_callbacks = settings.test_callbacks
            else:
                self.test_callbacks = []

            if hasattr(settings, 'test_files_max_number'):
                self._is_of_type('test_files_max_number', int)
                self.test_files_max_number = settings.test_files_max_number
            else:
                self.test_files_max_number = None

        else:
            self.test_step = None
            self.data_module_test = None
            self.merge_test_datasets = False
            self.test_batch_size = None
            self.test_callbacks = []
            self.test_dataset_parameters = None

        if not hasattr(settings, 'loss_options') or isinstance(settings.loss_options, type(None)):
            self.LossComputing = LossComputing(self.targets)
        else:
            self.LossComputing = LossComputing(self.targets, **settings.loss_options)

        try:
            assert not(self.data_module_train is None and self.data_module_test is None)
        except AssertionError as err:
            self._logger.exception('No data module has been provided. Set either a train or a test data module.')
            raise err

        if self.validating_ratio is not None:
            try:
                assert 0 < self.validating_ratio < 1
            except AssertionError as err:
                self._logger.exception('Validation ratio must belong to ]0,1[.')
                raise err

    def _has_mandatory(self, parameter, message):
        try:
            assert hasattr(self._settings, parameter)
        except AssertionError as err:
            self._logger.exception('Missing {param} : {msg}'.format(param=parameter, msg=message))
            raise err

    def _is_positive(self, parameter):
        message = 'Specification error on  {param}. It must be set above 0'.format(param=parameter)
        try:
            assert getattr(self._settings, parameter) > 0
        except AssertionError as err:
            self._logger.exception(message)
            raise err

    def _is_of_type(self, parameter, p_type):
        message = 'Specification error on  {param}. It must be of type {type}'.format(param=parameter,
                                                                                      type=p_type)
        try:
            assert isinstance(getattr(self._settings, parameter), p_type)
        except AssertionError as err:
            self._logger.exception(message)
            raise err

    def _is_function(self, parameter, n_args):
        message = 'Specification error on  {param}. It must be a function of {n_args} args'.format(param=parameter,
                                                                                                   n_args=n_args)
        try:
            assert inspect.isfunction(getattr(self._settings, parameter))
        except AssertionError as err:
            self._logger.exception(message)
            raise err
        try:
            assert len(inspect.getfullargspec(getattr(self._settings, parameter))[0]) == n_args
        except AssertionError as err:
            self._logger.exception(message)
            raise err

    def _check_data_module(self, data_module, train=True):
        """
        Check if the train or the test data module specified in the experiment setting file satisfy the required
        specifications.
        """
        if train:
            module_list = [VisionDomainAdaptationDataModule,
                           GLearnDomainAdaptationDataModule,
                           VisionDataModule,
                           GLearnDataModule]
        else:  # Domain adaptation is only used in the train context
            module_list = [VisionDataModule, GLearnDataModule]

        message = 'Specification error on  {module}. {context} data module must belong to {module_list}.'.format(
            context='Train' if train else 'Test', module=data_module['module'], module_list=module_list)
        try:
            assert data_module['module'] in module_list
        except AssertionError as err:
            self._logger.exception(message)
            raise err

        context = {'train': None, 'test': None}
        # Domain adaptation
        if data_module['module'] in [VisionDomainAdaptationDataModule, GLearnDomainAdaptationDataModule]:
            context['train'] = 'domain_adaptation'
            # No source will raise an error later
            data_module['source'] = data_module.get('source', {})

            # Target is not mandatory
            data_module['target'] = data_module.get('target', {})

            # Target path is not mandatory
            data_module['target']['paths'] = data_module['target'].get('paths', [])

            # Filters are not mandatory
            data_module['source']['image_filter'] = data_module['source'].get('image_filter', {})
            data_module['source']['event_filter'] = data_module['source'].get('event_filter', {})
            data_module['target']['image_filter'] = data_module['target'].get('image_filter', {})
            data_module['target']['event_filter'] = data_module['target'].get('event_filter', {})

            self._check_data_module_path(data_module['source']['paths'])
        # No domain adaptation
        elif data_module['module'] in [VisionDataModule, GLearnDataModule]:
            # Path is mandatory and will raise an error later if not set
            data_module['paths'] = data_module.get('paths', [])

            # Filters are not mandatory
            data_module['image_filter'] = data_module.get('image_filter', {})
            data_module['event_filter'] = data_module.get('event_filter', {})

            self._check_data_module_path(data_module['paths'])

        return context

    def _check_data_module_path(self, data_module_path):
        # Train (source) paths are mandatory for both train and test
        message = 'Specification error on  {param}. It must non-empty'.format(param="paths")
        try:
            assert data_module_path and isinstance(data_module_path, list)
        except AssertionError as err:
            self._logger.exception(message)
            raise err


class LitGLearnModule(LightningModule):
    def __init__(self, experiment):
        super().__init__()
        # TODO save hyperparameters
        # self.save_hyperparameters(dict from experiment)
        self.automatic_optimization = False
        self.experiment = experiment
        self.console_logger = logging.getLogger(__name__)
        self.grad_norm = 0

        # create network
        self.net = self.experiment.net_parameters_dic['model'](self.experiment.net_parameters_dic['parameters'])
        if self.local_rank == 0:
            self.console_logger.info(
                'network parameters number : {}'.format(compute_total_parameter_number(self.net))
            )
        self.train_metrics = torch.nn.ModuleDict()
        for task, param in self.experiment.targets.items():
            self.train_metrics[task] = torch.nn.ModuleDict()
            for name, metric in param['metrics'].items():
                self.train_metrics[task][name] = metric
        self.val_metrics = copy.deepcopy(self.train_metrics)

        # Following is mandatory. If loss_balancing is a nn.Module, it allows for a correct device setting
        # and the loss_balancing parameters checkpointing
        self.loss_balancing = self.experiment.loss_balancing
        self.test_data = {'output': [], 'dl1_params': []}

    def forward(self, x):
        return self.net(x)

    def reset_test_data(self):
        self.test_data = {'output': [], 'dl1_params': []}

    def training_step(self, batch, batch_idx):
        # Reset gradients
        optimizers = self.optimizers(use_pl_optimizer=True)
        if isinstance(optimizers, list):
            for optim in optimizers:
                optim.zero_grad()
        else:
            optimizers.zero_grad()

        if batch_idx == 0 and self.trainer.current_epoch == 0:
            self.console_logger.info(('Experiment running on {}'.format(self.device)))  # TODO handle multi gpus
            if self.device.type == 'cuda':
                self.console_logger.info('GPU name : {}'.format(torch.cuda.get_device_name(self.device.index)))

        output, labels, loss_data, loss = self.experiment.training_step(self, batch)

        self.manual_backward(loss)

        norm = 0
        for p in list(filter(lambda x: x.grad is not None, self.net.parameters())):
            norm += p.grad.data.norm(2).detach() ** 2
        self.grad_norm = norm ** (1. / 2)

        if isinstance(optimizers, list):
            for optim in optimizers:
                optim.step()
        else:
            optimizers.step()

        # log losses
        n_batches = len(self.trainer.train_dataloader)
        if (batch_idx + 1) % self.experiment.log_every_n_steps == 0:
            self.console_logger.info('Epoch[{}] Iteration[{}/{}]'.format(self.current_epoch, batch_idx+1, n_batches))
            # log losses
            for n, v in loss_data.items():
                self.console_logger.info('Training Loss ' + n + ' {}'.format(v))
            # log other metrics
            for task, all_metrics in self.train_metrics.items():
                for name, metric in all_metrics.items():
                    m_value = metric(output[task], labels[task])
                    self.console_logger.info('Training ' + name + ' {}'.format(m_value))
                    
        if isinstance(self.experiment.trainer_logger, TrainerTensorboardLogger):  # If TensorBoardLogger, add scalars to tensorboard
            if batch_idx == 0 and self.trainer.current_epoch == 0:
                self.logger.experiment.add_scalars('Training', {'Loss_' + n: v for n, v in loss_data.items()})

        self.log('Training', {'Loss_' + n: v for n, v in loss_data.items()}, on_step=False, on_epoch=True)
        training_loss = 0
        for v in loss_data.values():
            training_loss += v
        self.log('Loss', {'training': training_loss}, on_step=False, on_epoch=True)
        self.log('Loss_weighted', {'training': loss.detach()}, on_step=False, on_epoch=True)
        # log other metrics
        for task, all_metrics in self.train_metrics.items():
            for name, metric in all_metrics.items():
                m_value = metric(output[task], labels[task])
                self.log(name, {'training': m_value}, on_step=False, on_epoch=True)  # Lightning takes care of resetting

        
        return loss

    def training_epoch_end(self, outputs):
        lr_schedulers = self.lr_schedulers()
        if lr_schedulers is not None:
            lr_schedulers = [lr_schedulers] if not isinstance(lr_schedulers, list) else lr_schedulers
            for scheduler in lr_schedulers:
                if isinstance(scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    scheduler.step(self.trainer.callback_metrics["Loss_validating"])
                elif not isinstance(scheduler, DANNLR):  # DANNLR is handled in training_step_end
                    scheduler.step()

    def training_step_end(self, batch_parts):
        lr_schedulers = self.lr_schedulers()
        if lr_schedulers is not None:
            lr_schedulers = [lr_schedulers] if not isinstance(lr_schedulers, list) else lr_schedulers
            for scheduler in lr_schedulers:
                if isinstance(scheduler, DANNLR):
                    scheduler.step(self)

    def validation_step(self, batch, batch_idx):
        output, labels, loss_data, loss = self.experiment.eval_step(self, batch)
        # log losses
        self.log('Validating', {'Loss_' + n: v for n, v in loss_data.items()})
        val_loss = 0
        for n, v in loss_data.items():
            # self.console_logger.info('Validating ' + n + ' {}'.format(v))
            val_loss += v
        self.log('Loss', {'validating': val_loss})
        self.log('Loss_validating', loss.detach())
        self.log('Loss_weighted', {'validating': loss.detach()})
        # Accumulate metrics
        for task, all_metrics in self.val_metrics.items():
            for name, metric in all_metrics.items():
                metric(output[task], labels[task])

    def validation_epoch_end(self, *args, **kwargs):
        self.console_logger.info('Epoch[{}] Validation]'.format(self.current_epoch))
        # log metrics
        for task, all_metrics in self.val_metrics.items():
            for name, metric in all_metrics.items():
                m_value = metric.compute()
                self.log(name, {'validating': m_value})
                self.console_logger.info('Validating ' + name + ' {}'.format(m_value))
                metric.reset()  # We have to reset bc we manually log the metrics here (to log them in console)

    def test_step(self, batch, batch_idx):
        output, dl1_params = self.experiment.test_step(self, batch)
        self.test_data['output'].append(output)
        self.test_data['dl1_params'].append(dl1_params)

    def configure_optimizers(self):
        optim_keys = self.experiment.optimizer_dic.keys()
        self.optim_keys = optim_keys
        if 'network' in optim_keys:
            assert all(
                key not in optim_keys
                for key in ['feature', 'classifier', 'regressor']
            ), 'If you define an optimizer for the whole network, you cant also define one for a subpart of it.'

        if 'feature' in optim_keys:
            assert 'classifier' in optim_keys or 'regressor' in optim_keys, \
                'You need an optimizer for every subparts of the net.'

        optimizers = {}
        for key in self.experiment.optimizer_dic.keys():
            if key == 'network':
                optimizers[key] = self.experiment.optimizer_dic[key](self.net,
                                                                     self.experiment.optimizer_parameters[key])
            elif key == 'loss_balancing':
                assert isinstance(self.experiment.loss_balancing, torch.nn.Module)
                optimizers[key] = self.experiment.optimizer_dic[key](self.experiment.loss_balancing,
                                                                     self.experiment.optimizer_parameters[key])
            else:
                try:
                    assert getattr(self.net, key, None) is not None
                except AssertionError as e:
                    self.console_logger.error(e)
                    print(key)
                    print(self.net)
                    raise e
                optimizers[key] = self.experiment.optimizer_dic[key](getattr(self.net, key),
                                                                     self.experiment.optimizer_parameters[key])

        if self.experiment.lr_schedulers is not None:
            schedulers = []
            for net_param, scheduler_param in self.experiment.lr_schedulers.items():
                for scheduler, params in scheduler_param.items():
                    if optimizers[net_param] is not None:
                        schedulers.append({
                            'scheduler': scheduler(optimizers[net_param], **params),
                            'name': 'lr_' + net_param
                        })
        else:
            schedulers = None

        return list(optimizers.values()), schedulers

    def log_from_console_logger(self, output: dict, labels: dict, loss: dict, loss_data: dict, batch_idx: int) -> None:
        n_batches = len(self.trainer.train_dataloader)
        if (batch_idx + 1) % self.experiment.log_every_n_steps == 0:
            self.console_logger.info('Epoch[{}] Iteration[{}/{}]'.format(self.current_epoch, batch_idx+1, n_batches))
            # log losses
            for n, v in loss_data.items():
                self.console_logger.info('Training Loss ' + n + ' {}'.format(v))
            # log other metrics
            for task, all_metrics in self.train_metrics.items():
                for name, metric in all_metrics.items():
                    m_value = metric(output[task], labels[task])
                    self.console_logger.info('Training ' + name + ' {}'.format(m_value))

def build_argparser():
    """
    Construct main argument parser for the ``gammalearn`` script

    :return:
    argparser: `argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        description="Run a GammaLearn experiment from a configuration file. An experiment can be a training, a testing or both. See examples configuration files in the examples folder."
    )
    parser.add_argument("configuration_file", help="path to configuration file")
    parser.add_argument('--fast_debug', help='log useful information for debug purpose',
                        action='store_true')
    parser.add_argument("--logfile", help="whether to write the log on disk", action="store_true")
    parser.add_argument('--version', action='version', version=_version)

    return parser


def main():
    # For better performance (if the input size does not vary from a batch to another)
    cudnn.benchmark = True

    # At the beginning of the main process, local_rank is set to None.
    # When multiple processes are running in parallel (e.g. while loading some data), each process will be assigned to a
    # positive valued local_rank. When each sub-process is started, it will run the main() function. Setting this
    # variable at the beginning ensure that some actions will only occur once and not within the other sub-process.
    local_rank = os.getenv('LOCAL_RANK')

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('gammalearn')

    # Parse script arguments
    logger.info('parse arguments')

    parser = build_argparser()
    args = parser.parse_args()
    configuration_file = args.configuration_file
    fast_debug = args.fast_debug
    logfile = args.logfile

    # Update logging config
    LOGGING_CONFIG['handlers']['console']['formatter'] = 'console_debug' if fast_debug else 'console_info'
    LOGGING_CONFIG['loggers']['gammalearn']['level'] = 'DEBUG' if fast_debug else 'INFO'
    logging.config.dictConfig(LOGGING_CONFIG)

    logger = logging.getLogger('gammalearn')

    # load settings file
    if local_rank is None:
        logger.info(f'load settings from {configuration_file}')
    spec = importlib.util.spec_from_file_location("settings", configuration_file)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    # check config and prepare experiment
    experiment = Experiment(settings)

    # prepare folders
    if local_rank is None:
        logger.info('prepare folders')
        prepare_experiment_folder(experiment.main_directory, experiment.experiment_name)

    if logfile:
        LOGGING_CONFIG['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'filename': '{}/{}/{}.log'.format(settings.main_directory,
                                              settings.experiment_name,
                                              settings.experiment_name),
            'mode': 'w',
            'formatter': 'detailed_debug' if fast_debug else 'detailed_info'
        }
        LOGGING_CONFIG['loggers']['gammalearn']['handlers'].append('file')
        logging.config.dictConfig(LOGGING_CONFIG)

    if local_rank is None:
        logger.info('gammalearn {}'.format(_version))
        # save config(settings)
        logger.info('save configuration file')
        shutil.copyfile(configuration_file, '{}/{}/{}_settings.py'.format(experiment.main_directory,
                                                                          experiment.experiment_name,
                                                                          experiment.experiment_name))
        # dump settings
        dump_experiment_config(experiment)

    # set seed
    if experiment.random_seed is not None:
        pl.trainer.seed_everything(experiment.random_seed)

    geometries = []
    # Load train data module
    if experiment.train is True:
        gl_data_module_train = experiment.data_module_train['module'](experiment)
        gl_data_module_train.setup_train()
        train_dataloaders = gl_data_module_train.train_dataloader()
        val_dataloaders = gl_data_module_train.val_dataloader()
        get_dataset_geom(gl_data_module_train.train_set, geometries)
    else:
        train_dataloaders = None
        val_dataloaders = None
    # Load test data module
    if experiment.test is True:
        if experiment.data_module_test is not None:
            gl_data_module_test = experiment.data_module_test['module'](experiment)
            gl_data_module_test.setup_test()
            test_dataloaders = gl_data_module_test.test_dataloaders()
            get_dataset_geom(gl_data_module_test.test_sets, geometries)
        else:  # If no test data module, use validation data from train data module
            try:
                assert val_dataloaders is not None
            except AssertionError as err:
                logger.exception('No test data module is provided and validation data loader is None.')
                raise err
            test_dataloaders = [val_dataloaders]
    else:
        test_dataloaders = None
    
    # testing if all geometries are equal
    if len(set(geometries)) != 1:
        raise WrongGeometryError("There are different geometries in the train and the test datasets")

    experiment.net_parameters_dic = inject_geometry_into_parameters(experiment.net_parameters_dic, geometries[0])

    # Define multiprocessing start method
    try:
        assert torch.multiprocessing.get_start_method() == experiment.mp_start_method
    except AssertionError:
        torch.multiprocessing.set_start_method(experiment.mp_start_method, force=True)
    if local_rank is None:
        logger.info('mp start method: {}'.format(torch.multiprocessing.get_start_method()))

    # Reset seed
    if experiment.random_seed is not None:
        pl.trainer.seed_everything(experiment.random_seed)

    if local_rank is None:
        logger.info('Save net definition file')
        if experiment.net_definition_file is not None:
            shutil.copyfile(experiment.net_definition_file, '{}/{}/nets.py'.format(experiment.main_directory,
                                                                               experiment.experiment_name))

    # load lightning module
    gl_lightning_module = LitGLearnModule(experiment)
    checkpoint_callback = ModelCheckpoint(**experiment.checkpointing_options)

    # Log learning rates
    callbacks = [
        checkpoint_callback,
        LearningRateMonitor(logging_interval='epoch'),
    ]

    if experiment.monitor_device and experiment.gpus not in [None, 0]:
        callbacks.append(DeviceStatsMonitor())

    callbacks.extend(experiment.training_callbacks)
    callbacks.extend(experiment.test_callbacks)

    # prepare logger
    experiment.trainer_logger.setup(experiment, gl_lightning_module)
    if local_rank is None:
        logger.info('{} run directory: {} '.format(experiment.trainer_logger.type, experiment.trainer_logger.get_run_directory(experiment)))

    # Prepare profiler
    if experiment.profiler is not None:
        profiler = experiment.profiler['profiler'](
            dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
            filename=os.path.join(experiment.experiment_name + '.prof'),
            **experiment.profiler['options']
        )
    else:
        profiler = None

    # Run !
    if fast_debug:
        trainer = pl.Trainer(fast_dev_run=True, gpus=-1, profiler=profiler)
        trainer.fit(gl_lightning_module,
                    train_dataloaders=train_dataloaders,
                    val_dataloaders=val_dataloaders)
        # TODO remove when lightning bug is fixed
        if experiment.profiler is not None:
            profiler = experiment.profiler['profiler'](
                dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                filename=os.path.join(experiment.experiment_name + '.prof'),
                **experiment.profiler['options'])
            trainer.profiler = profiler

        trainer.test(gl_lightning_module, dataloaders=test_dataloaders)
    else:
        if experiment.train:
            trainer = pl.Trainer(
                default_root_dir=os.path.join(experiment.main_directory, experiment.experiment_name),
                accelerator=experiment.accelerator, devices=experiment.gpus,
                strategy=experiment.strategy,
                max_epochs=experiment.max_epochs,
                logger=experiment.trainer_logger.logger,
                log_every_n_steps=experiment.log_every_n_steps,
                check_val_every_n_epoch=experiment.check_val_every_n_epoch,
                callbacks=callbacks, profiler=profiler,
            )
            logger.info('Rank {}: Train model'.format(gl_lightning_module.local_rank))
            trainer.fit(gl_lightning_module,
                        train_dataloaders=train_dataloaders,
                        val_dataloaders=val_dataloaders,
                        ckpt_path=experiment.checkpoint_path)
            if experiment.test:
                trainer = pl.Trainer(
                    default_root_dir=os.path.join(experiment.main_directory, experiment.experiment_name),
                    accelerator=experiment.accelerator, devices=1,  # Force 1 GPU for test
                    strategy=experiment.strategy,
                    logger=experiment.trainer_logger.logger,
                    callbacks=callbacks, profiler=profiler,
                )
                logger.info('Rank {}: Test model'.format(gl_lightning_module.local_rank))
                for dataloader in test_dataloaders:
                    # TODO remove when lightning bug is fixed
                    if experiment.profiler is not None:
                        profiler = experiment.profiler['profiler'](
                            dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                            filename=os.path.join(experiment.experiment_name + '.prof'),
                            **experiment.profiler['options'])
                        trainer.profiler = profiler

                    trainer.test(gl_lightning_module,
                                 dataloaders=dataloader)
                    gl_lightning_module.reset_test_data()
        elif experiment.test:
            trainer = pl.Trainer(
                default_root_dir=os.path.join(experiment.main_directory, experiment.experiment_name),
                accelerator=experiment.accelerator, devices=1,  # Force 1 GPU for test
                # Recommended with ddp strategy see https://gitlab.in2p3.fr/gammalearn/gammalearn/-/issues/101
                strategy=experiment.strategy,
                logger=experiment.trainer_logger.logger,
                callbacks=callbacks
            )
            logger.info('Rank {}: Test model'.format(gl_lightning_module.local_rank))
            assert experiment.checkpoint_path is not None, 'To test a model w/o training, there must be a checkpoint'
            map_location = torch.device('cpu') if experiment.gpus == 0 else None
            ckpt = torch.load(experiment.checkpoint_path, map_location=map_location)
            gl_lightning_module.load_state_dict(ckpt['state_dict'], strict=False)
            for dataloader in test_dataloaders:
                # TODO remove when lightning bug is fixed
                if experiment.profiler is not None:
                    profiler = experiment.profiler['profiler'](
                        dirpath=os.path.join(experiment.main_directory, experiment.experiment_name),
                        filename=os.path.join(experiment.experiment_name + '.prof'),
                        **experiment.profiler['options'])
                    trainer.profiler = profiler

                trainer.test(gl_lightning_module, dataloaders=dataloader)
                gl_lightning_module.reset_test_data()


if __name__ == '__main__':
    main()

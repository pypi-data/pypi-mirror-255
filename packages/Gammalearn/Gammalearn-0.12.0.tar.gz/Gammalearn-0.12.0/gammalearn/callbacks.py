import os

import torch
import torch.nn as nn
from torch.utils.data import Subset
from pytorch_lightning.callbacks import Callback
from pytorch_lightning.loggers import TensorBoardLogger
from torchmetrics import Accuracy, ConfusionMatrix
from torchmetrics.functional.pairwise import pairwise_cosine_similarity
from torchvision import transforms
import torchvision.utils as t_utils
import numpy as np
import pandas as pd
import tables
from ctapipe.instrument import CameraGeometry
from ctapipe.visualization import CameraDisplay
from ctapipe.io import HDF5TableWriter
from lstchain.io import write_dl2_dataframe
from lstchain.reco.utils import add_delta_t_key
from lstchain.io.io import dl1_params_lstcam_key
from PIL import Image
from indexedconv.engine import IndexedConv
from indexedconv.utils import create_index_matrix, img2mat, pool_index_matrix, build_hexagonal_position
from astropy.table import Table

from gammalearn.constants import SOURCE, TARGET
import gammalearn.utils as utils
import gammalearn.criterions as criterions
import gammalearn.datasets as dsets
import gammalearn.version as gl_version
import gammalearn.constants as csts

import matplotlib.pyplot as plt
from pathlib import Path


class LogUncertaintyLogVars(Callback):
    """
    Callback to send loss log vars of the Uncertainty estimation method to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_epoch_end(self, trainer, pl_module):
        if isinstance(pl_module.experiment.loss_balancing, criterions.MultiLossBalancing):
            log_vars = pl_module.experiment.loss_balancing.log_vars
            vars_dict = {}

            targets = pl_module.experiment.targets.copy()
            for k, v in targets.items():
                if not v['mt_balancing']:
                    targets.pop(k)

            for i, task in enumerate(targets.keys()):
                vars_dict['Logvar_' + task] = log_vars[i].detach().cpu()
            pl_module.log('Log_vars', vars_dict, on_epoch=True, on_step=False)


class LogUncertaintyPrecisions(Callback):
    """
    Callback to send loss precisions of the Uncertainty estimation method to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_epoch_end(self, trainer, pl_module):
        if isinstance(pl_module.experiment.loss_balancing, criterions.UncertaintyWeighting):
            log_vars = pl_module.experiment.loss_balancing.log_vars
            vars_dict = {}

            targets = pl_module.experiment.targets.copy()
            for k, v in targets.items():
                if not v['mt_balancing']:
                    targets.pop(k)

            for i, task in enumerate(targets.keys()):
                vars_dict['Precision_' + task] = torch.exp(-log_vars[i].detach().cpu())
            pl_module.log('Precisions', vars_dict, on_epoch=True, on_step=False)


class LogLossWeighting(Callback):
    """
    Callback to send loss weight coefficients to logger
    Parameters
    ----------
    Returns
    -------
    """

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if isinstance(pl_module.experiment.loss_balancing, criterions.MultiLossBalancing):
            weights_dict = pl_module.experiment.loss_balancing.weights_dict
            log_weights_dict = {}
            for task in weights_dict.keys():
                log_weights_dict[task] = weights_dict[task].detach().cpu()
            pl_module.log('Loss_weight_per_task', log_weights_dict, on_epoch=False, on_step=True)


class LogGradientNormPerTask(Callback):
    """
    Callback to send the tasks gradient norm to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if isinstance(pl_module.experiment.loss_balancing, criterions.MultiLossBalancing):
            if pl_module.experiment.loss_balancing.requires_gradients:
                gradients_dict = pl_module.experiment.loss_balancing.gradients_dict
                log_gradients_dict = {}
                for task in gradients_dict.keys():
                    log_gradients_dict[task] = gradients_dict[task].norm().detach().cpu()
                pl_module.log('Gradient_norm_per_task', log_gradients_dict, on_epoch=False, on_step=True)


class LogGradientCosineSimilarity(Callback):
    """
    Callback to send the tasks gradient cosine similarity to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if isinstance(pl_module.experiment.loss_balancing, criterions.MultiLossBalancing):
            if pl_module.experiment.loss_balancing.requires_gradients:
                gradients = pl_module.experiment.loss_balancing.gradients
                similarity = pairwise_cosine_similarity(gradients, gradients)
                log_similarity_dict = {}
                targets = pl_module.experiment.targets.copy()
                for i, task_i in enumerate(targets):
                    for j, task_j in enumerate(targets):
                        if i < j:  # Only upper triangular matrix as similarity is symmetric
                            log_similarity_dict[task_i+'_'+task_j] = similarity[i, j]
                pl_module.log(f'Gradient_cosine_similarity', log_similarity_dict, on_epoch=False, on_step=True)


class LogGradNormWeights(Callback):
    """
    Callback to send GradNorm weights to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx, dataloader_idx):
        if isinstance(pl_module.experiment.loss_balancing, criterions.GradNormBalancing):
            if pl_module.global_step % pl_module.experiment.log_every_n_steps == 0:
                weights = pl_module.experiment.loss_balancing.weights
                weights_dict = {}
                for i, task in enumerate(pl_module.experiment.targets.keys()):
                    weights_dict['Gradnorm_w_' + task] = weights[i]
                pl_module.log('Gradnorm_weights', weights_dict, on_step=True, on_epoch=False)


class LogModelWeightNorm(Callback):
    """
    Callback to send sum of squared weigths of the network to logger
    Parameters
    ----------
    Returns
    -------

    """
    def on_train_epoch_end(self, trainer, pl_module):
        weights = 0
        for name, param in pl_module.net.named_parameters():
            if 'weight' in name:
                weights += torch.sum(param.data ** 2)
        pl_module.log('weights', weights, on_epoch=True, on_step=False)


class LogModelParameters(Callback):
    """
    Callback to send the network parameters to logger
    Parameters
    ----------
    Returns
    -------
    """

    def on_train_epoch_end(self, trainer, pl_module):
        if isinstance(pl_module.loggers, TensorBoardLogger):
            for name, param in pl_module.net.named_parameters():
                pl_module.logger.experiment.add_histogram(name, param.detach().cpu(),
                                                        bins='tensorflow',
                                                        global_step=pl_module.current_epoch)
        else:
            # In that case, trainer_logger.watch is implemented in the experiment runner
            pass


def make_activation_sender(pl_module, name):
    """
    Creates the adapted activations sender to tensorboard
    Parameters
    ----------
    pl_module (LightningModule): the tensorboardX writer
    name (string) : name of the layer which activation is logged

    Returns
    -------
    An adapted function
    """

    def send(m, input, output):
        """
        The function to send the activation of a module to tensorboard
        Parameters
        ----------
        m (nn.Module): the module (eg nn.ReLU, ...)
        input
        output

        Returns
        -------

        """
        pl_module.logger.experiment.add_histogram(name, output.detach().cpu(),
                                                  bins='tensorflow', global_step=pl_module.current_epoch)

    return send


class LogReLUActivations(Callback):
    """
    Callback to send activations to logger
    Parameters
    ----------
    Returns
    -------
    """
    def setup(self, trainer, pl_module, stage):
        self.hooks = []

    def on_train_epoch_start(self, trainer, pl_module):
        for name, child in pl_module.net.named_children():
            if isinstance(child, nn.ReLU):
                sender = make_activation_sender(pl_module, name)
                self.hooks.append(child.register_forward_hook(sender))

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        for hook in self.hooks:
            hook.remove()


def make_linear_gradient_logger(pl_module, name):
    def log_grad(m, grad_input, grad_output):
        pl_module.logger.experiment.add_histogram(name + 'grad_in', grad_input[0].data.cpu(),
                                                  bins='tensorflow', global_step=pl_module.current_epoch)
    return log_grad


class LogLinearGradient(Callback):
    """
    Callback to send gradients to logger
    Parameters
    ----------
    Returns
    -------
    """

    def setup(self, trainer, pl_module, stage):
        self.hooks = []

    def on_train_epoch_start(self, trainer, pl_module):
        for name, child in pl_module.net.named_modules():
            if isinstance(child, nn.Linear):
                grad_logger = make_linear_gradient_logger(pl_module, name)
                self.hooks.append(child.register_full_backward_hook(grad_logger))

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        for hook in self.hooks:
            hook.remove()


def make_feature_logger(pl_module, name, index_matrices):
    def log_features(m, input, output):
        if output.dim() == 3:
            features = output.detach().cpu().clone()
            images_list = []
            index_matrix = index_matrices[features.shape[-1]]
            pixel_pos = np.array(build_hexagonal_position(index_matrix.squeeze().squeeze()))
            pix_area = np.full(features.shape[-1], 6/np.sqrt(3)*0.5**2)
            # TODO load meta from datafile
            geom = CameraGeometry.from_table(
                Table(
                    {
                        'pix_id': np.arange(features.shape[-1]),
                        'pix_x': list(map(lambda x: x[0], pixel_pos)),
                        'pix_y': list(map(lambda x: x[1], pixel_pos)),
                        'pix_area': pix_area,
                    },
                    meta={
                        'PIX_TYPE': 'hexagonal',
                        'PIX_ROT': 0,
                        'CAM_ROT': 0,
                    }
                )
            )

            for b, batch in enumerate(features):
                for c, channel in enumerate(batch):
                    label = '{}_b{}_c{}'.format(name, b, c)
                    ax = plt.axes(label=label)
                    ax.set_aspect('equal', 'datalim')
                    disp = CameraDisplay(geom, ax=ax)
                    disp.image = channel
                    disp.add_colorbar()
                    ax.set_title(label)
                    canvas = plt.get_current_fig_manager().canvas
                    canvas.draw()
                    pil_img = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
                    images_list.append(transforms.ToTensor()(pil_img))

            grid = t_utils.make_grid(images_list)

            pl_module.logger.experiment.add_image('Features_{}'.format(name),
                                                  grid, pl_module.current_epoch)
    return log_features


class LogFeatures(Callback):

    def setup(self, trainer, pl_module, stage):
        self.hooks = []
        self.index_matrices = {}
        index_matrix = create_index_matrix(pl_module.camera_parameters['nbRow'],
                                           pl_module.camera_parameters['nbCol'],
                                           pl_module.camera_parameters['injTable'])
        n_pixels = int(torch.sum(torch.ge(index_matrix[0, 0], 0)).data)
        self.index_matrices[n_pixels] = index_matrix
        idx_matx = index_matrix
        while n_pixels > 1:
            idx_matx = pool_index_matrix(idx_matx, kernel_type=pl_module.camera_parameters['layout'])
            n_pixels = int(torch.sum(torch.ge(idx_matx[0, 0], 0)).data)
            self.index_matrices[n_pixels] = idx_matx

    def on_train_epoch_start(self, trainer, pl_module):
        for name, child in pl_module.net.named_children():
            if isinstance(child, nn.ReLU):
                feature_logger = make_feature_logger(pl_module, name, self.index_matrices)
                self.hooks.append(child.register_forward_hook(feature_logger))

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        for hook in self.hooks:
            hook.remove()


class LogGradientNorm(Callback):
    """
    Callback to send the gradient total norm to logger
    Parameters
    ----------
    Returns
    -------
    """
    def on_train_epoch_end(self, trainer, pl_module):
        pl_module.log('Gradient_norm', pl_module.grad_norm, on_epoch=True, on_step=False)


class WriteDL2Files(Callback):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """
    def on_test_end(self, trainer, pl_module):
        # Retrieve test data
        merged_outputs = pd.concat([pd.DataFrame(utils.prepare_dict_of_tensors(output))
                                    for output in pl_module.test_data['output']], ignore_index=True)
        merged_dl1_params = pd.concat([pd.DataFrame(utils.prepare_dict_of_tensors(dl1))
                                       for dl1 in pl_module.test_data['dl1_params']], ignore_index=True)

        dl2_params = utils.post_process_data(merged_outputs, merged_dl1_params, pl_module.experiment.dataset_parameters)

        if pl_module.experiment.data_module_test is None or pl_module.experiment.merge_test_datasets:
            # Test has been done on the validation set or test dl1 have been merged in datasets by particle type

            ratio = pl_module.experiment.validating_ratio if pl_module.experiment.data_module_test is None else 1.0

            # Retrieve MC config information
            mc_configuration = {}

            def fetch_dataset_info(d):
                if isinstance(d, torch.utils.data.ConcatDataset):
                    for d_c in d.datasets:
                        fetch_dataset_info(d_c)
                elif isinstance(d, Subset):
                    fetch_dataset_info(d.dataset)
                elif issubclass(pl_module.experiment.dataset_class, dsets.BaseLSTDataset):
                    particle_type = d.dl1_params['mc_type'][0]
                    if particle_type not in mc_configuration:
                        mc_configuration[particle_type] = {'mc_energies': [], 'run_configs': []}
                    if d.simu:
                        mc_energies = d.trig_energies
                        np.random.shuffle(mc_energies)
                        mc_energies = mc_energies[:int(len(mc_energies) * ratio)]
                        d.run_config['mcheader']['num_showers'] *= ratio
                        mc_configuration[particle_type]['mc_energies'].extend(mc_energies)
                    mc_configuration[particle_type]['run_configs'].append(d.run_config)
                else:
                    pl_module.console_logger.error('Unknown dataset type, MC configuration cannot be retrieved')
                    raise ValueError

            for dataloader in trainer.test_dataloaders:
                fetch_dataset_info(dataloader.dataset)

            # Write one file per particle type
            for mc_type in mc_configuration:
                particle_mask = merged_dl1_params['mc_type'] == mc_type

                gb_file_path = pl_module.experiment.main_directory + '/' + pl_module.experiment.experiment_name + '/' + \
                               pl_module.experiment.experiment_name + '_' + str(mc_type) + '.h5'
                if os.path.exists(gb_file_path):
                    os.remove(gb_file_path)

                writer = HDF5TableWriter(gb_file_path)
                dl1_version = []
                ctapipe_version = []
                runlist = []

                for config in mc_configuration[mc_type]['run_configs']:
                    try:
                        dl1_version.append(config['metadata']['LSTCHAIN_VERSION'])
                    except Exception:
                        pl_module.console_logger.warning('There is no LSTCHAIN_VERSION in run config')
                    try:
                        ctapipe_version.append(config['metadata']['CTAPIPE_VERSION'])
                    except Exception:
                        pl_module.console_logger.warning('There is no CTAPIPE_VERSION in run config')
                    try:
                        runlist.extend(config['metadata']['SOURCE_FILENAMES'])
                    except Exception:
                        pl_module.console_logger.warning('There is no SOURCE_FILENAMES in run config')
                    try:
                        writer.write('simulation/run_config', config['mcheader'])
                    except Exception:
                        pl_module.console_logger.warning('Issue when writing run config')
                writer.close()

                try:
                    assert len(set(dl1_version)) == 1
                except AssertionError:
                    warning_msg = 'There should be strictly one dl1 data handler version in dataset but there are {}'\
                        .format(set(dl1_version))
                    pl_module.console_logger.warning(warning_msg)
                    dl1_version = 'Unknown'
                else:
                    dl1_version = dl1_version[0]

                try:
                    assert len(set(ctapipe_version)) == 1
                except AssertionError:
                    warning_msg = 'There should be strictly one ctapipe version in dataset but there are {}'\
                        .format(set(ctapipe_version))
                    pl_module.console_logger.warning(warning_msg)
                    ctapipe_version = 'Unknown'
                else:
                    ctapipe_version = ctapipe_version[0]

                try:
                    assert runlist
                except AssertionError:
                    pl_module.console_logger.warning('Run list is empty')

                metadata = {
                    'LSTCHAIN_VERSION': dl1_version,
                    'CTAPIPE_VERSION': ctapipe_version,
                    'mc_type': mc_type,
                    'GAMMALEARN_VERSION': gl_version.__version__,
                }

                with tables.open_file(gb_file_path, mode='a') as file:
                    for k, item in metadata.items():
                        if k in file.root._v_attrs and type(file.root._v_attrs) is list:
                            attribute = file.root._v_attrs[k].extend(metadata[k])
                            file.root._v_attrs[k] = attribute
                        else:
                            file.root._v_attrs[k] = metadata[k]
                    if runlist and '/simulation' in file:
                        file.create_array('/simulation', 'runlist', obj=runlist)

                pd.DataFrame(
                    {
                        'mc_trig_energies': np.array(mc_configuration[mc_type]['mc_energies'])
                    }
                ).to_hdf(gb_file_path,
                         key='triggered_events')

                if mc_type == csts.REAL_DATA_ID:
                    # Post dl2 ops for real data
                    dl2_params = add_delta_t_key(dl2_params)

                utils.write_dataframe(merged_dl1_params[particle_mask], outfile=gb_file_path,
                                      table_path=dl1_params_lstcam_key)
                write_dl2_dataframe(dl2_params[particle_mask], gb_file_path)
        else:
            # Prepare output
            if pl_module.experiment.dl2_path is not None:
                output_dir = pl_module.experiment.dl2_path
            else:
                output_dir = pl_module.experiment.main_directory + '/' + pl_module.experiment.experiment_name + '/dl2/'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dataset = trainer.test_dataloaders[0].dataset
            output_name = os.path.basename(dataset.hdf5_file_path)
            output_name = output_name.replace('dl1', 'dl2')
            output_path = os.path.join(output_dir, output_name)
            if os.path.exists(output_path):
                os.remove(output_path)

            mc_type = merged_dl1_params['mc_type'][0]
            mc_energies = dataset.trig_energies

            utils.write_dl2_file(dl2_params, dataset, output_path, mc_type=mc_type, mc_energies=mc_energies)


class WriteAutoEncoderDL1(Callback):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """
    def on_test_end(self, trainer, pl_module):
        # Set output dataframe
        output_df = pd.DataFrame()

        # Fill the output dataframe with the errors between the AE outputs and the ground truths
        merged_outputs = utils.merge_list_of_dict(pl_module.test_data['output'])
        for k, v in merged_outputs.items():
            output_df[k] = torch.cat(v).detach().to('cpu').numpy()

        # Also fill with the dl1 parameters if they are available
        merged_dl1_params = utils.merge_list_of_dict(pl_module.test_data['dl1_params'])
        for k, v in merged_dl1_params.items():
            if k in ['mc_core_x', 'mc_core_y', 'tel_pos_x', 'tel_pos_y', 'tel_pos_z', 'mc_x_max']:
                output_df[k] = 1000 * torch.cat(v).detach().to('cpu').numpy()
            else:
                output_df[k] = torch.cat(v).detach().to('cpu').numpy()

        # Get output path
        if pl_module.experiment.data_module_test is None:
            # Test has to be done on the validation set: Write one file
            output_path = os.path.join(pl_module.experiment.main_directory, pl_module.experiment.experiment_name,
                                       pl_module.experiment.experiment_name + '_ae_validation_results.h5')
        else:
            # One output file per dl1 file
            output_dir = os.path.join(pl_module.experiment.main_directory,
                                      pl_module.experiment.experiment_name,
                                      'ae_test_results')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            dataset = trainer.test_dataloaders[0].dataset
            output_name = os.path.basename(dataset.hdf5_file_path)
            output_name = output_name.replace('dl1', 'ae_results')
            output_path = os.path.join(output_dir, output_name)

        if os.path.exists(output_path):
            os.remove(output_path)

        # Write output dataframe
        output_df.to_hdf(output_path, key='data')


class WriteData(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.output_dir_default = None
        self.output_file_default = None

    def get_output_path(self, experiment) -> Path:
        # Prepare output folder
        if experiment.output_dir is not None:
            output_dir = Path(experiment.output_dir)
        else:
            output_dir = Path(experiment.main_directory, experiment.experiment_name, self.output_dir_default)

        output_dir.mkdir(exist_ok=True)

        # Prepare output file
        if experiment.output_file is not None:
            output_file = Path(experiment.output_file)
        else:
            output_file = Path(self.output_file_default)

        # Get output path
        output_path = output_dir.joinpath(output_file)

        if output_path.exists():
            output_path.unlink()
        
        return output_path


class WriteAutoEncoder(WriteData):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """

    def __init__(self) -> None:
        super().__init__()
        self.output_dir_default = 'ae_results'
        self.output_file_default = 'ae.csv'

    def on_test_end(self, trainer, pl_module):
        # Set output dataframe
        output_df = pd.DataFrame()

        # Fill the output dataframe with the errors between the AE outputs and the ground truths
        merged_outputs = utils.merge_list_of_dict(pl_module.test_data['output'])
        for k, v in merged_outputs.items():
            output_df[k] = torch.cat(v).detach().to('cpu').numpy()

        # Get output path
        output_path = self.get_output_path(pl_module.experiment)

        # Write output dataframe
        output_df.to_csv(output_path, index=False)


class WriteAccuracy(WriteData):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """

    def __init__(self) -> None:
        super().__init__()
        self.output_dir_default = 'accuracy_results'
        self.output_file_default = 'accuracy.csv'

    def on_test_end(self, trainer, pl_module):
        # Get prediction and ground truth
        predictions, targets = torch.empty((0, )), torch.empty((0, ))
        for batch in pl_module.test_data['output']:
            predictions = torch.hstack((predictions, torch.argmax(batch['outputs']['class'], dim=1).cpu()))
            targets = torch.hstack((targets, batch['labels']['class'].cpu()))
        predictions, targets = predictions.flatten().to(torch.int64), targets.flatten().to(torch.int64)

        # Compute accuracy
        num_classes = pl_module.experiment.targets['class']['output_shape']
        accuracy = Accuracy(num_classes=num_classes, multiclass=True, average=None)
        output_df = pd.DataFrame({'Accuracy': accuracy(predictions, targets).numpy()}, index=[np.arange(num_classes)])

        # Get output path
        output_path = self.get_output_path(pl_module.experiment)

        # Write output dataframe
        output_df.to_csv(output_path, index=False)


class WriteAccuracyDomain(WriteData):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """

    def __init__(self) -> None:
        super().__init__()
        self.output_dir_default = 'accuracy_domain_results'
        self.output_file_default = 'accuracy_domain.csv'
        
    def on_test_end(self, trainer, pl_module):
        # Get prediction and ground truth
        predictions = torch.empty((0, ))
        for batch in pl_module.test_data['output']:
            if 'outputs' in batch.keys():
                predictions = torch.hstack((predictions, torch.argmax(batch['outputs']['domain_class'], dim=1).cpu()))
            else:
                predictions = torch.hstack((predictions, torch.argmax(batch['domain_class'], dim=1).cpu()))
        predictions = predictions.flatten().to(torch.int64)
        targets_source = (torch.ones(predictions.shape) * SOURCE).to(torch.int64)
        targets_target = (torch.ones(predictions.shape) * TARGET).to(torch.int64)

        # Compute accuracy
        num_classes = 2
        accuracy = Accuracy(num_classes=num_classes)
        output_df = pd.DataFrame(
            [
                accuracy(predictions, targets_source).numpy(),
                accuracy(predictions, targets_target).numpy()
            ],
            index=[np.arange(2)]
        )

        # Get output path
        output_path = self.get_output_path(pl_module.experiment)

        # Write output dataframe
        output_df.to_csv(output_path, index=False)


class WriteConfusionMatrix(WriteData):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """

    def __init__(self) -> None:
        super().__init__()
        self.output_dir_default = 'confusion_matrix_results'
        self.output_file_default = 'confusion_matrix.csv'

    def on_test_end(self, trainer, pl_module):
        # Get prediction and ground truth
        predictions, targets = torch.empty((0, )), torch.empty((0, ))
        for batch in pl_module.test_data['output']:
            predictions = torch.hstack((predictions, torch.argmax(batch['outputs']['class'], dim=1).cpu()))
            targets = torch.hstack((targets, batch['labels']['class'].cpu()))
        predictions, targets = predictions.flatten().to(torch.int64), targets.flatten().to(torch.int64)

        # Compute accuracy
        num_classes = pl_module.experiment.targets['class']['output_shape']
        cm = ConfusionMatrix(num_classes=num_classes)
        output_df = pd.DataFrame(cm(predictions, targets).numpy(), index=[np.arange(num_classes)],
                                 columns=np.arange(num_classes))

        # Get output path
        output_path = self.get_output_path(pl_module.experiment)

        # Write output dataframe
        output_df.to_csv(output_path, index=False)


class WriteADistance(WriteData):
    """
    Callback to produce testing result data files
    Parameters
    ----------
    trainer (Trainer)
    pl_module (LightningModule)

    Returns
    -------
    """

    def __init__(self) -> None:
        super().__init__()
        self.output_dir_default = 'a_distance_results'
        self.output_file_default = 'a_distance.csv'

    def on_test_end(self, trainer, pl_module):
        # Get prediction
        predictions, targets = torch.empty((0,)), torch.empty((0,))
        for batch in pl_module.test_data['output']:
            predictions = torch.hstack((predictions, torch.argmax(batch['outputs']['domain_class'], dim=1).cpu()))
            targets = torch.hstack((targets, batch['labels']['domain_class'].cpu()))
        predictions, targets = predictions.flatten().to(torch.int64), targets.flatten().to(torch.int64)

        # Compute accuracy
        accuracy_metric = Accuracy(num_classes=2)

        # Compute a-distance
        accuracy = accuracy_metric(predictions, targets)
        error = 1. - accuracy
        a_distance = torch.abs((2. * (1. - 2. * error)).mean())  # distance is 0 when classifier converges to 0.5 accuracy
        output_df = pd.DataFrame({'accuracy': [accuracy.numpy()], 'A_distance': [a_distance.numpy()]})

        # Get output path
        output_path = self.get_output_path(pl_module.experiment)

        # Write output dataframe
        output_df.to_csv(output_path, index=False)

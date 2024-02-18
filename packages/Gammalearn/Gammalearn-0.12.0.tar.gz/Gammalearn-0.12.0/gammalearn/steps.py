import torch
from gammalearn.utils import BaseW
from gammalearn.criterions import DANNLoss


def get_training_step_mae(**kwargs):

    def training_step_mae(module, batch):
        """
        The training operations for one batch for vanilla mt learning
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """

        # Load data
        images = batch['image']

        if kwargs['add_pointing']:
            pointing = torch.stack((batch['dl1_params']['alt_tel'],
                                    batch['dl1_params']['az_tel']), dim=1).to(torch.float32)
            loss = module.net(images, pointing)
        else:
            loss = module.net(images)

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return None, None, {'autoencoder': loss.detach().item()}, loss

    return training_step_mae


def get_eval_step_mae(**kwargs):

    def validation_step_mae(module, batch):
        """
        The training operations for one batch for vanilla mt learning
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """

        # Load data
        images = batch['image']

        if kwargs['add_pointing']:
            pointing = torch.stack((batch['dl1_params']['alt_tel'],
                                    batch['dl1_params']['az_tel']), dim=1).to(torch.float32)
            loss = module.net(images, pointing)
        else:
            loss = module.net(images)

        return None, None, {'autoencoder': loss.detach().item()}, loss

    return validation_step_mae


def get_training_step_mt(**kwargs):

    def training_step_mt(module, batch):
        """
        The training operations for one batch for vanilla mt learning
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, False, kwargs.get('add_pointing', False))
        outputs = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(outputs, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return outputs, labels, loss_data, loss

    return training_step_mt


def get_training_step_dann(**kwargs):

    def training_step_dann(module, batch):
        """
        The training operations for one batch
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """
        # Load data
        data = run_model(module, batch, False, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        # Add the target domain into the output and labels
        output['domain_class'] = torch.cat([output['domain_class'], data['outputs_target']['domain_class']])
        labels['domain_class'] = torch.cat([labels['domain_class'], data['labels_target']['domain_class']])

        # Update domain loss mask if necessary
        if DANNLoss.fetch_domain_conditional_from_targets(module.experiment.targets):  # If domain conditional is True
            labels_class = torch.cat([data['labels_source']['class'], data['labels_target']['class']])  # Get labels
            DANNLoss.set_domain_loss_mask_from_targets(module.experiment.targets, labels_class)  # Set mask

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        return output, labels, loss_data, loss

    return training_step_dann


def get_training_step_deepjdot(**kwargs):

    def training_step_deepjdot(module, batch):
        """
        The training operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, True, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        # The alignment task is optimized using the latent features of the source and the target.
        output['deepjdot'] = data['latent_features'][0]
        labels['deepjdot'] = data['latent_features'][1]

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return training_step_deepjdot


def get_training_step_deepcoral(**kwargs):

    def training_step_deepcoral(module, batch):
        """
        The training operations for one batch for vanilla mt learning
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, True, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        output['deepcoral'] = data['latent_features'][0]
        labels['deepcoral'] = data['latent_features'][1]

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return training_step_deepcoral


def get_training_step_mkmmd(**kwargs):

    def training_step_mkmmd(module, batch):
        """
        The training operations for one batch for vanilla mt learning
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, True, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        output['mkmmd'] = data['latent_features'][0]
        labels['mkmmd'] = data['latent_features'][1]

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return training_step_mkmmd


def get_training_step_mt_gradient_penalty(**kwargs):

    def training_step_mt_gradient_penalty(module, batch):
        """
        The training operations for one batch for vanilla mt learning with gradient penalty
        Parameters
        ----------
        module: LightningModule
        batch

        Returns
        -------

        """

        # Load data
        images = batch['image']
        labels = batch['label']
        images.requires_grad = True

        if kwargs.get('add_pointing', False):
            pointing = torch.stack((batch['dl1_params']['alt_tel'], batch['dl1_params']['az_tel']), dim=1)
            output = module.net({'data': images, 'pointing': pointing})
        else:
            output = module.net(images)

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            gradient_x = torch.autograd.grad(loss, images, retain_graph=True)[0]
            penalty = torch.mean((torch.norm(gradient_x.view(gradient_x.shape[0], -1), 2, dim=1) - 1) ** 2)
            loss += penalty * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return training_step_mt_gradient_penalty


def get_eval_step_mt(**kwargs):

    def eval_step_mt(module, batch):
        """
        The validating operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, False, kwargs.get('add_pointing', False))
        outputs = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        # Compute loss and quality measures
        loss, loss_data = module.experiment.LossComputing.compute_loss(outputs, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        return outputs, labels, loss_data, loss

    return eval_step_mt


def get_eval_step_dann(**kwargs):

    def eval_step_dann(module, batch):
        """
        The validating operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, False, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        # Add the target domain into the output and labels
        output['domain_class'] = torch.cat([output['domain_class'], data['outputs_target']['domain_class']])
        labels['domain_class'] = torch.cat([labels['domain_class'], data['labels_target']['domain_class']])

        # Update domain loss mask if necessary
        if DANNLoss.fetch_domain_conditional_from_targets(module.experiment.targets):  # If domain conditional is True
            labels_class = torch.cat([data['labels_source']['class'], data['labels_target']['class']])  # Get labels
            DANNLoss.set_domain_loss_mask_from_targets(module.experiment.targets, labels_class)  # Set mask

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        return output, labels, loss_data, loss

    return eval_step_dann


def get_eval_step_deepjdot(**kwargs):

    def eval_step_deepjdot(module, batch):
        """
        The validating operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, True, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        # The alignment task is optimized using the latent features of the source and the target.
        output['deepjdot'] = data['latent_features'][0]
        labels['deepjdot'] = data['latent_features'][1]

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return eval_step_deepjdot


def get_eval_step_deepcoral(**kwargs):

    def eval_step_deepcoral(module, batch):
        """
        The validating operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, True, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        output['deepcoral'] = data['latent_features'][0]
        labels['deepcoral'] = data['latent_features'][1]

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return eval_step_deepcoral


def get_eval_step_mkmmd(**kwargs):

    def eval_step_mkmmd(module, batch):
        """
        The validating operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """

        # Load data
        data = run_model(module, batch, True, kwargs.get('add_pointing', False))
        output = data['outputs_source']
        labels = data['labels_source']
        dl1_params = data['dl1_params_source']

        output['mkmmd'] = data['latent_features'][0]
        labels['mkmmd'] = data['latent_features'][1]

        # Compute loss
        loss, loss_data = module.experiment.LossComputing.compute_loss(output, labels, module)
        loss = module.experiment.loss_balancing(loss, module)
        loss = sum(loss.values())

        if module.experiment.regularization is not None:
            loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

        return output, labels, loss_data, loss

    return eval_step_mkmmd


def get_test_step_mt(**kwargs):

    def test_step_mt(module, batch):
        """
        The test operations for one batch
        Parameters
        ----------
        module
        batch

        Returns
        -------

        """
        data = run_model(module, batch, True, kwargs.get('add_pointing', False), train=False)
        if kwargs.get('add_labels', False):
            outputs = data['outputs_source']
            labels = data['labels_source']
            output = {'outputs': outputs, 'labels': labels}
        else:
            output = data['outputs_source']
        dl1_params = batch.get('dl1_params', None)

        return output, dl1_params

    return test_step_mt


def format_labels(output_dict):
    """
    Format the labels to be consistent with data augmentation. Data augmentation will produce a batch of size
    Nx...xCxRxW but the model needs the batch to be of size NxCxRxW with N the batch size, C the channel size, R the
    row size and W the width size.
    """

    # We define the 'labels' variable as a List, and two scenarios may be encountered:
    #   - Either we are in the context of domain adaptation, then we have source and target labels (target labels
    #   contain at least the domain labels, as it is generated in the corresponding dataset class)
    #   - Or there is no domain adaptation, and the classical labels are stored in the source labels (cf the 'run_model'
    #   function)
    labels = ['labels_source', 'labels_target'] \
        if output_dict.get('labels_target', None) is not None else ['labels_source']

    # For each label, the processing is different, as they could be scalar, images, ...
    for label in labels:
        for k, v in output_dict[label].items():
            if k in ['class', 'domain_class']:  # Scalar
                output_dict[label][k] = v.flatten(start_dim=0)
            elif k == 'autoencoder':  # Images
                output_dict[label][k] = v.flatten(end_dim=-4)
            elif k in ['energy', 'impact', 'direction', 'deepjdot', 'deepcoral', 'mkmmd']:
                # A priori not subjected to data augmentation, otherwise this function must be modified
                pass
            else:
                # In order to make sure that the developers have thought about this, we raise an error if the label has
                # not been specified in this function.
                raise ValueError('Unknown target')

    return output_dict


def run_model(module, batch, requires_latent_features=False, requires_pointing=False, forward_params=None, train=True):
    """
    If the training is not in the context of domain adaptation, the information will be stored in xxx_source.
    Parameters
    ----------
        module: () The current module.
        batch: (torch.tensor) The current batch of data.
        requires_latent_features: (bool) Creates a hook to get the latent space. The model must respect the following
        design rule and have either a 'module.net.main_task_model.feature' or a 'module.net.feature' component.
        requires_pointing: (bool) Whether to include the pointing information as the model's argument.
        forward_params: (dict) Allows to pass the model's forward function extra parameters. The model must respect the
        corresponding design rule of the model's forward function.
        train: (bool) Whether the current step is a training or a test step.
    """
    hook = None  # To fetch latent features
    latent_features = []

    if requires_latent_features:
        # Define hook to get latent features
        def get_latent_features(module, input, output):
            if isinstance(output, (tuple, list)):
                # UNet encoder outputs a tuple, and the latent space is located in the last element of the tuple
                latent_features.append(output[-1])
            else:
                latent_features.append(output)

        if 'main_task' in module.experiment.net_parameters_dic['parameters']:
            # When DANN is used, it creates a 'main_task'.
            if hasattr(module.net.main_task_model, 'feature'):
                hook = module.net.main_task_model.feature.register_forward_hook(get_latent_features)
        else:
            # When DANN is not used (for example, a single UNet encoder).
            if hasattr(module.net, 'feature'):
                hook = module.net.feature.register_forward_hook(get_latent_features)

    # Load data
    inputs_source = inputs_target = None
    labels_source = labels_target = None
    outputs_target = None
    dl1_params_source = dl1_params_target = None

    if 'image' in batch.keys():  # No domain adaptation
        inputs_source = batch['image']
        # Nx...xCxWxH -> N'xCxWxH
        inputs_source = inputs_source.flatten(end_dim=-4) if len(inputs_source.shape) > 3 else inputs_source
    if 'image_source' in batch.keys():
        inputs_source = batch['image_source']
        # Nx...xCxWxH -> N'xCxWxH
        inputs_source = inputs_source.flatten(end_dim=-4) if len(inputs_source.shape) > 3 else inputs_source
    if 'image_target' in batch.keys():
        inputs_target = batch['image_target']
        # Nx...xCxWxH -> N'xCxWxH
        inputs_target = inputs_target.flatten(end_dim=-4) if len(inputs_target.shape) > 3 else inputs_target
    if 'label' in batch.keys():  # No domain adaptation
        labels_source = batch['label']
    if 'label_source' in batch.keys():
        labels_source = batch['label_source']
    if 'label_target' in batch.keys():
        labels_target = batch['label_target']
    if 'dl1_params' in batch.keys():  # No domain adaptation
        dl1_params_source = batch['dl1_params']
    if 'dl1_params_source' in batch.keys():
        dl1_params_source = batch['dl1_params_source']
    if 'dl1_params_target' in batch.keys():
        dl1_params_target = batch['dl1_params_target']

    forward_params = {} if forward_params is None else forward_params
    pointing_source = pointing_target = None

    if requires_pointing:
        # Include the altitude - azimuth (alt - az) information into the network.
        if 'dl1_params' in batch.keys():
            alt_tel = batch['dl1_params']['alt_tel']
            az_tel = batch['dl1_params']['az_tel']
            pointing_source = torch.stack((alt_tel, az_tel), dim=1).to(torch.float32)
        if 'dl1_params_source' in batch.keys():
            alt_tel = batch['dl1_params_source']['alt_tel']
            az_tel = batch['dl1_params_source']['az_tel']
            pointing_source = torch.stack((alt_tel, az_tel), dim=1).to(torch.float32)
        if 'dl1_params_target' in batch.keys():
            alt_tel = batch['dl1_params_target']['alt_tel']
            az_tel = batch['dl1_params_target']['az_tel']
            pointing_target = torch.stack((alt_tel, az_tel), dim=1).to(torch.float32)

    # Monitor forward parameters
    forward_params['pointing'] = pointing_source  # TODO: deal with pointing_target
    for _, v in module.experiment.targets.items():
        if v.get('loss_weight', None) is not None:
            if isinstance(v['loss_weight'], BaseW):
                if v['loss_weight'].apply_on_grads:
                    forward_params['weight_grads'] = v['loss_weight'].get_weight(module.trainer)

    outputs_source = module.net(inputs_source, **forward_params)
    if inputs_target is not None:
        forward_params['pointing'] = pointing_target
        outputs_target = module.net(inputs_target, **forward_params)

    if hook is not None:
        # Remove hook to avoid accumulation
        hook.remove()

    output_dict = {
        'inputs_source': inputs_source,
        'inputs_target': inputs_target,
        'labels_source': labels_source,
        'labels_target': labels_target,
        'dl1_params_source': dl1_params_source,
        'dl1_params_target': dl1_params_target,
        'outputs_source': outputs_source,
        'outputs_target': outputs_target,
        'latent_features': latent_features,
    }

    if train:
        output_dict = format_labels(output_dict)

    return output_dict

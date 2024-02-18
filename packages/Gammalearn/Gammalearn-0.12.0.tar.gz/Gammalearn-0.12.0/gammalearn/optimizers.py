import torch.optim as optim
import torch
from gammalearn.utils import compute_dann_hparams
from torch.optim.lr_scheduler import _LRScheduler
import re


def load_sgd(net, parameters):
    """
    Load the SGD optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'lr' in parameters.keys(
    ), 'Missing learning rate for the optimizer !'
    assert 'weight_decay' in parameters.keys(
    ), 'Missing weight decay for the optimizer !'
    return optim.SGD(net.parameters(), **parameters)


def load_adam(net, parameters):
    """
    Load the Adam optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'lr' in parameters.keys(
    ), 'Missing learning rate for the optimizer !'

    return optim.Adam(net.parameters(), **parameters)


def load_adam_w(net, parameters):
    """
    Load the Adam optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'lr' in parameters.keys(
    ), 'Missing learning rate for the optimizer !'

    return optim.AdamW(net.parameters(), **parameters)


def load_rmsprop(net, parameters):
    """
    Load the RMSprop optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'lr' in parameters.keys(
    ), 'Missing learning rate for the optimizer !'

    return optim.RMSprop(net.parameters(), **parameters)


def load_per_layer_sgd(net, parameters):
    """
    Load the SGD optimizer with a different learning rate for each layer.
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'lr' in parameters.keys(), 'Missing learning rate for the optimizer !'
    assert 'weight_decay' in parameters.keys(), 'Missing weight decay for the optimizer !'
    assert 'alpha' in parameters.keys(), 'Missing alpha !'

    lr_default = parameters['lr']
    alpha = parameters.pop('alpha')

    feature_modules = []  # The feature parameters
    base_modules = []  # The other parameters
    for name, module in net.named_modules():
        if isinstance(module, torch.nn.Linear) or isinstance(module, torch.nn.Conv2d):
            if name.split('.')[0] == 'feature':
                feature_modules.append(module)
            else:
                base_modules.append(module)

    feature_lr = [lr_default / (alpha ** layer) for layer in range(1, len(feature_modules) + 1)]
    feature_lr.reverse()

    parameter_group = [{'params': p.parameters()} for p in base_modules]
    parameter_group += [{'params': p.parameters(), 'lr': lr} for p, lr in zip(feature_modules, feature_lr)]

    return torch.optim.SGD(parameter_group, **parameters)


def freeze(net, parameters):
    """
    Freeze the network parameters
    Parameters
    ----------
    net (nn.Module): the network or the subnetwork (e.g. feature)
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    for p in net.parameters():
        p.requires_grad = False

    return None


def prime_optimizer(net: torch.nn.Module, parameters: dict) -> torch.optim.Optimizer:
    """
    Load the optimizer for Masked AutoEncoder fine tuning (transformers)
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    num_blocks = len(list(net.encoder.children())) + 1
    layer_scales = [parameters['layer_decay'] ** (num_blocks - i) for i in range(num_blocks+1)]

    no_weight_decay = ['pos_embedding', 'additional_tokens']

    param_groups = {}

    for n, p in net.named_parameters():
        if p.requires_grad:
            # Non weight decay
            if p.ndim == 1 or n in no_weight_decay:
                this_decay = 0.
            else:
                this_decay = None

            layer_id = get_layer_id_for_prime(n)
            group_name = str(layer_id) + '_' + str(this_decay)
            if group_name not in param_groups:
                layer_scale = layer_scales[layer_id]
                param_groups[group_name] = {
                    # 'lr_scale': layer_scale,
                    'lr': layer_scale * parameters['optimizer_parameters']['lr'],
                    'params': []
                }
                if this_decay is not None:
                    param_groups[group_name]['weight_decay'] = this_decay
            param_groups[group_name]['params'].append(p)
    return parameters['optimizer'](list(param_groups.values()), **parameters['optimizer_parameters'])


def get_layer_id_for_prime(name: str) -> int:
    """
    Retrieve GammaPhysNetPrime layer id from parameter name
    """
    if any(layer in name for layer in ['pos_embedding', 'patch_projection']):
        return 0
    else:
        try:
            block = re.findall(r'enc_block_\d', name)[0]
            block = int(block.split('_')[-1]) + 1
            return block
        except IndexError:
            return -1


#############################
# Regularization strategies #
#############################


def l1(net):
    """
    Simple L1 penalty.
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """
    penalty = 0
    for param in net.parameters():
        penalty += torch.norm(param, 1)

    return penalty


def l2(net):
    """
    Simple L2 penalty.
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """
    penalty = 0
    for param in net.parameters():
        penalty += torch.norm(param, 2)**2

    return penalty / 2


def elastic(net):
    """
    Elastic penalty (L1 + L2).
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """

    return l1(net) + l2(net)


def srip(net):
    """
    Spectral Restricted Isometry Property (SRIP) regularization penalty. See https://arxiv.org/abs/1810.09102
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """
    penalty = 0
    for n, W in net.named_parameters():
        if W.ndimension() >= 2:
            # print('{} : {}'.format(n, W.ndimension()))
            cols = W[0].numel()
            rows = W.shape[0]
            w1 = W.view(-1, cols)
            wt = torch.transpose(w1, 0, 1)
            if rows > cols:
                m = torch.matmul(wt, w1)
                ident = torch.eye(cols, cols, device=W.device)
            else:
                m = torch.matmul(w1, wt)
                ident = torch.eye(rows, rows, device=W.device)

            w_tmp = m - ident
            b_k = torch.rand(w_tmp.shape[1], 1, device=W.device)

            v1 = torch.matmul(w_tmp, b_k)
            norm1 = torch.norm(v1, 2)
            v2 = torch.div(v1, norm1)
            v3 = torch.matmul(w_tmp, v2)

            penalty += (torch.norm(v3, 2))**2
    return penalty


class DANNLR(_LRScheduler):
    def __init__(self, optimizer, domain_classifier=False):
        self.domain_classifier = domain_classifier

        # Attach optimizer
        if not isinstance(optimizer, optim.Optimizer):
            raise TypeError('{} is not an Optimizer'.format(
                type(optimizer).__name__))
        self.optimizer = optimizer

    def step(self, module) -> None:
        lambda_p, mu_p = compute_dann_hparams(module)
        if self.domain_classifier:
            new_lr = mu_p / lambda_p
        else:
            new_lr = mu_p

        for param_group in self.optimizer.param_groups:
            param_group['lr'] = new_lr

        self.last_lr = new_lr

    def get_lr(self) -> float:
        return self.last_lr

    def state_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if key != 'optimizer'}

    def load_state_dict(self, state_dict) -> None:
        self.__dict__.update(state_dict)

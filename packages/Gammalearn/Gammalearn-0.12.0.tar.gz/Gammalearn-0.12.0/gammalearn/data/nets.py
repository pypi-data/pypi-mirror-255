import logging
import math
from modulefinder import Module
import torch
from torch.nn.functional import upsample
from torchvision.models import resnet18, ResNet, EfficientNet, MobileNetV2, MobileNetV3
from torchvision.models.vision_transformer import VisionTransformer,  EncoderBlock
import torchvision
import torch.nn as nn
import torch.nn.functional as F
import indexedconv.utils as cvutils
from indexedconv.engine import IndexedConv, IndexedMaxPool2d, IndexedAveragePool2d
from gammalearn.utils import (get_camera_layout_from_geom,
                              get_2d_sincos_pos_embedding_from_patch_centroids,
                              get_2d_sincos_pos_embedding_from_grid,
                              get_patch_indices_and_centroids_from_geometry,
                              get_patch_indices_and_grid,
                              get_torch_weights_from_lightning_checkpoint)
from ctapipe.instrument import CameraGeometry
import numpy as np
from collections import OrderedDict
from typing import Union, Tuple, Any


class BNDA(nn.Module):
    """
    
    """
    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1, affine: bool = True, 
                 track_running_stats: bool = True):
        super().__init__()
        self.bn_source = nn.BatchNorm2d(num_features, eps, momentum, affine, track_running_stats)
        self.bn_target = nn.BatchNorm2d(num_features, eps, momentum, affine, track_running_stats)

    def forward(self, x):
        xs, xt = x[:x.shape[0]//2], x[x.shape[0]//2:]
        return torch.cat((self.bn_source(xs), self.bn_target(xt)), dim=0)


class SqueezeExcite(nn.Module):
    """Squeeze and excite the output of a convolution as described in the paper https://arxiv.org/abs/1709.01507


    """
    def __init__(self, num_channels, ratio):
        super(SqueezeExcite, self).__init__()
        reducted_channels = int(num_channels / ratio)
        self.reduction = nn.Linear(num_channels, reducted_channels)
        self.expand = nn.Linear(reducted_channels, num_channels)

    def forward(self, x):
        out = x.mean(dim=tuple(range(x.dim())[2:]))

        out = F.relu(self.reduction(out))
        out = torch.sigmoid(self.expand(out))

        out_size = out.size() + tuple(1 for _ in range(x.dim() - 2))
        out = x * out.view(out_size)

        return out


class SelfAttention(nn.Module):
    """Self attention layer as described in the SAGAN paper https://arxiv.org/abs/1805.08318

    """
    def __init__(self, channels, ratio):
        super(SelfAttention, self).__init__()
        self.conv_f = nn.Conv1d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_g = nn.Conv1d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_h = nn.Conv1d(channels, channels, kernel_size=1, bias=False)

        self.gamma = nn.Parameter(torch.tensor(0.))

    def forward(self, x):
        batch = x.shape[0]
        channel = x.shape[1]
        f = self.conv_f(x.view(batch, channel, -1))
        g = self.conv_g(x.view(batch, channel, -1))
        h = self.conv_h(x.view(batch, channel, -1))

        s = torch.matmul(f.permute(0, 2, 1), g)

        beta = nn.functional.softmax(s, dim=-1)

        o = torch.matmul(beta, h.permute(0, 2, 1)).permute(0, 2, 1)

        return (self.gamma * o.view(x.shape) + x).contiguous()


# TODO check if it  works
class SelfAttention2d(nn.Module):
    """Self attention layer as described in the SAGAN paper https://arxiv.org/abs/1805.08318

    """
    def __init__(self, channels, ratio):
        super(SelfAttention2d, self).__init__()
        self.conv_f = nn.Conv2d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_g = nn.Conv2d(channels, channels // ratio, kernel_size=1, bias=False)
        self.conv_h = nn.Conv2d(channels, channels, kernel_size=1, bias=False)

        self.gamma = nn.Parameter(torch.tensor(0.))

    def forward(self, x):
        batch = x.shape[0]
        channel = x.shape[1]
        f = self.conv_f(x.view(batch, channel, -1))
        g = self.conv_g(x.view(batch, channel, -1))
        h = self.conv_h(x.view(batch, channel, -1))

        s = torch.matmul(f.permute(0, 2, 3, 1), g)

        beta = nn.functional.softmax(s, dim=(-2, -1))

        o = torch.matmul(beta, h.permute(0, 2, 3, 1)).permute(0, 2, 3, 1)

        return (self.gamma * o.view(x.shape) + x).contiguous()


class SpatialAttention(nn.Module):
    """
    Spatial attention layer as described in https://arxiv.org/pdf/2001.07645.pdf and implemented in
    https://github.com/sunjesse/shape-attentive-unet/blob/master/models/attention_blocks.py
    """
    def __init__(self, channels):
        super(SpatialAttention, self).__init__()
        self.down = nn.Conv1d(channels, channels // 2, kernel_size=1, bias=False)
        self.phi = nn.Conv1d(channels // 2, 1, kernel_size=1, bias=True)
        self.bn = nn.BatchNorm1d(channels // 2)

        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                n = m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm1d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x):
        out = F.relu(self.bn(self.down(x.view(x.shape[0], x.shape[1], -1))))
        out = torch.sigmoid(self.phi(out))
        return out.reshape((x.shape[0], 1,) + x.shape[2:])


class DualAttention(nn.Module):
    """
    Dual attention layer as described in https://arxiv.org/pdf/2001.07645.pdf and implemented in
    https://github.com/sunjesse/shape-attentive-unet/blob/master/models/attention_blocks.py
    """
    def __init__(self, in_channels, ratio):
        super(DualAttention, self).__init__()
        self.se_module = SqueezeExcite(in_channels, ratio)
        self.spa_module = SpatialAttention(in_channels)

    def forward(self, x):
        se = self.se_module(x)
        spa = self.spa_module(x)
        return se * (spa + 1)


class _IndexedConvLayer(nn.Sequential):
    def __init__(self, layer_id, index_matrix, num_input, num_output, non_linearity=nn.ReLU,
                 pooling=IndexedAveragePool2d, pooling_kernel='Hex', pooling_radius=1, pooling_stride=2,
                 pooling_dilation=1, pooling_retina=False,
                 batchnorm=True, drop_rate=0, bias=True,
                 kernel_type='Hex', radius=1, stride=1, dilation=1, retina=False):
        super(_IndexedConvLayer, self).__init__()
        self.drop_rate = drop_rate
        indices = cvutils.neighbours_extraction(index_matrix, kernel_type, radius, stride, dilation, retina)
        self.index_matrix = cvutils.pool_index_matrix(index_matrix, kernel_type=pooling_kernel, stride=1)
        self.add_module('cv'+layer_id, IndexedConv(num_input, num_output, indices, bias))
        if pooling is not None:
            p_indices = cvutils.neighbours_extraction(self.index_matrix, pooling_kernel, pooling_radius, pooling_stride,
                                                      pooling_dilation, pooling_retina)
            self.index_matrix = cvutils.pool_index_matrix(self.index_matrix, kernel_type=pooling_kernel,
                                                          stride=pooling_stride)
            self.add_module('pool'+layer_id, pooling(p_indices))
        if batchnorm:
            self.add_module('bn'+layer_id, nn.BatchNorm1d(num_output))
        if non_linearity is not None:
            self.add_module(non_linearity.__name__ + layer_id, non_linearity())

    def forward(self, x):
        new_features = super(_IndexedConvLayer, self).forward(x)
        if self.drop_rate > 0:
            new_features = F.dropout(new_features, p=self.drop_rate, training=self.training)
        return new_features


class _Regressor(nn.Module):
    def __init__(self, tasks_name, tasks_output, num_features, num_layers, factor, non_linearity=nn.ReLU,
                 batchnorm=True, drop_rate=0):
        super().__init__()
        for i, (task, output) in enumerate(zip(tasks_name, tasks_output)):
            t = nn.Sequential()
            for l in range(1, num_layers):
                if l == 1:
                    t.add_module('lin' + str(l) + '_' + task, nn.Linear(num_features, num_features // factor))
                else:
                    t.add_module('lin' + str(l) + '_' + task, nn.Linear(num_features // ((l - 1) * factor),
                                                                        num_features // (l * factor)))
                if batchnorm:
                    t.add_module('bn' + str(l) + '_' + task, nn.BatchNorm1d(num_features // (l * factor)))
                t.add_module(non_linearity.__name__ + str(l) + '_' + task, non_linearity())

                if drop_rate > 0:
                    t.add_module('drop' + str(l) + '_' + task, nn.Dropout(p=drop_rate))
            if num_layers > 1:
                t.add_module('output_' + task, nn.Linear(num_features // ((num_layers - 1) * factor), output))
            else:
                t.add_module('output_' + task, nn.Linear(num_features, output))
            self.add_module(task, t)

    def forward(self, x):
        out = []
        for t in self.children():
            out.append(t(x))
        return torch.cat(out, dim=1)
    

class _BaseModule(nn.Module):
    def __init__(self):
        super().__init__()

    def check_normalization(self, normalization: Tuple[torch.nn.Module, dict]) -> Tuple[torch.nn.Module, dict]:
        if normalization is not None:
            if not isinstance(normalization, tuple):
                normalization = (normalization, {})
        return normalization

    def add_normalization(self, module: torch.nn.Sequential, layer_name: str, num_channels: torch.Tensor, 
                          normalization: Tuple[torch.nn.Module, dict]) -> None:
        """
        Function to add normalization layer to a module. 
        """
        if normalization is not None:
            if normalization[0] == torch.nn.BatchNorm1d:
                normalization[1]['num_features'] = num_channels
                
            elif normalization[0] == torch.nn.BatchNorm2d:
                normalization[1]['num_features'] = num_channels

            elif normalization[0] == torch.nn.LayerNorm:
                return NotImplementedError
            
            elif normalization[0] == torch.nn.InstanceNorm2d:
                normalization[1]['num_features'] = num_channels

            elif normalization[0] == torch.nn.GroupNorm:
                normalization[1]['num_channels'] = num_channels
                
            elif normalization[0] == BNDA:
                normalization[1]['num_features'] = num_channels

            else:
                raise ValueError('Unknown normalization')
            
            module.add_module(normalization[0].__name__ + layer_name, normalization[0](**normalization[1]))

    def check_activation(self, activation: Tuple[torch.nn.Module, dict]) -> Tuple[torch.nn.Module, dict]:
        if activation is not None:
            if not isinstance(activation, tuple):
                activation = (activation, {})
        return activation

    def add_activation(self, module: torch.nn.Sequential, layer_name: str, activation: Tuple[torch.nn.Module, dict]) -> None:
        """
        Function to add activation layer to a module.
        """
        if activation is not None:
            module.add_module(activation[0].__name__ + layer_name, activation[0](**activation[1]))

    def check_initialization(self, initialization: Tuple[Any, dict]) -> Tuple[Any, dict]:
        if initialization is not None:
            if not isinstance(initialization, tuple):
                initialization = (initialization, {})
        return initialization
            
    def initialize_weights(self, modules: torch.nn.Module, method: Any = (torch.nn.init.kaiming_uniform_, {'mode': 'fan_out'})) -> None:
        for m in modules:
            if isinstance(m, nn.Conv2d) or isinstance(m, IndexedConv):
                method[0](m.weight, **method[1])

    def freeze_weights(self, weights: torch.nn.Module, freeze: bool = False):
        if freeze:
            for w in weights.parameters():
                w.requires_grad = False


class _ResidualLayerIndexed(_BaseModule):
    def __init__(self, in_features: int, out_features: int, index_matrix, downsample: bool=False, pre_activation: bool=True, 
                 kernel_type: str='Hex', normalization: Tuple[nn.Module, dict]=None, non_linearity: Tuple[nn.Module, dict]=(nn.ReLU, {})):
        super().__init__()
        stride = 2 if downsample else 1
        self.pooled_matrix = cvutils.pool_index_matrix(index_matrix, kernel_type=kernel_type) if downsample else index_matrix
        indices_cv1 = cvutils.neighbours_extraction(index_matrix, stride=stride)
        indices_cv2 = cvutils.neighbours_extraction(self.pooled_matrix)

        self.shortcut = nn.Sequential()
        if downsample:
            self.add_normalization(self.shortcut, '_shortcut', in_features, normalization)
            self.add_activation(self.shortcut,'_shortcut', non_linearity)
            self.shortcut.add_module('cv_shortcut', IndexedConv(in_features, out_features, indices_cv1))
        else:
            self.shortcut.add_module('id', nn.Identity())

        self.conv_block = nn.Sequential()
        if pre_activation:
            self.add_normalization(self.conv_block,  '1', in_features, normalization)
            self.add_activation(self.conv_block, '1', non_linearity)

        self.conv_block.add_module('cv1', IndexedConv(in_features, out_features, indices_cv1))
        self.add_normalization(self.conv_block, '2', out_features, normalization)
        self.add_activation(self.conv_block, '2', non_linearity)
        self.conv_block.add_module('cv2', IndexedConv(out_features, out_features, indices_cv2))

    def forward(self, x):
        return self.conv_block(x) + self.shortcut(x)


class _ResidualLayerCartesian(_BaseModule):
    """
    Implementation of the residual block for interpolated CTA images (cartesian grid).
    """
    def __init__(self, in_features: int, out_features: int, downsample: bool=False, pre_activation: bool=True, 
                 normalization: Tuple[nn.Module, dict]=None, non_linearity: Tuple[nn.Module, dict]=(nn.ReLU, {})):
        super().__init__()
        self.shortcut = nn.Sequential()
        if downsample:
            stride = 2
            self.add_normalization(self.shortcut, '_shortcut', in_features, normalization)
            self.add_activation(self.shortcut, '_shortcut', non_linearity)
            self.shortcut.add_module('cv_shortcut', nn.Conv2d(in_features, out_features, kernel_size=3, stride=stride, padding=1))
        else:
            stride = 1
            self.shortcut.add_module('id', nn.Identity())

        self.conv_block = nn.Sequential()
        if pre_activation:
            self.add_normalization(self.conv_block,  '1', in_features, normalization)
            self.add_activation(self.conv_block, '1', non_linearity)

        self.conv_block.add_module('cv1', nn.Conv2d(in_features, out_features, kernel_size=3, stride=stride, padding=1))
        self.add_normalization(self.conv_block, '2', out_features, normalization)
        self.add_activation(self.conv_block, '2', non_linearity)
        self.conv_block.add_module('cv2', nn.Conv2d(out_features, out_features, kernel_size=3, padding=1))  # stride=1 here

    def forward(self, x):
        return self.conv_block(x) + self.shortcut(x)


class ResNetAttention(_BaseModule):
    """
    ResNet like Network based on https://arxiv.org/abs/1603.05027, CIFAR version with full pre-activation,
    augmented with attention (see backbone definition :
    https://www.scitepress.org/Link.aspx?doi=10.5220/0010297405340544)
    """

    def __init__(self, net_parameters_dic):
        """

        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network

        """
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.ResNetAttention')

        num_layers = net_parameters_dic['num_layers']
        num_channels = [net_parameters_dic['num_channels']]
        num_channels.extend(net_parameters_dic['block_features'])
        attention = net_parameters_dic['attention_layer']
        non_linearity = net_parameters_dic['non_linearity']
        output_size = net_parameters_dic['output_size']
        normalization = net_parameters_dic.get('normalization', None)
        initialization = net_parameters_dic.get('initialization', 'kaiming')
        freeze = net_parameters_dic.get('freeze', False)
        self.num_features = num_channels[-1]
        self.non_linearity = non_linearity() if not isinstance(non_linearity, tuple) else non_linearity[0](**non_linearity[1])

        # Check normalization and activation and convert to tuple if necessary
        normalization = self.check_normalization(normalization)
        non_linearity = self.check_activation(non_linearity)

        # ResNet backbone
        self.feature = nn.Sequential()

        # Layer 0
        self.feature.add_module('cv0', nn.Conv2d(num_channels[0], 16, 3, padding=1))
        self.add_activation(self.feature, '0', non_linearity)

        # blocks
        for i, (n_in, n_out) in enumerate(zip(num_channels[:-1], num_channels[1:])):
            if i == 0:
                for n in range(1, num_layers + 1):
                    pre_activation = False if n == 1 else True

                    layer = _ResidualLayerCartesian(n_out, n_out,
                                                    pre_activation=pre_activation,
                                                    normalization=normalization,
                                                    non_linearity=non_linearity)
                    self.feature.add_module('block' + str(i) + '_layer' + str(n), layer)
            else:
                for n in range(1, num_layers + 1):
                    in_features = n_in if n == 1 else n_out
                    downsample = True if n == 1 else False

                    layer = _ResidualLayerCartesian(in_features, n_out, 
                                                    downsample=downsample, 
                                                    normalization=normalization,
                                                    non_linearity=non_linearity)
                    self.feature.add_module('block' + str(i) + '_layer' + str(n), layer)

            if attention is not None:
                self.feature.add_module('attention_block' + str(i), attention[0](n_out, **attention[1]))

        self.add_activation(self.feature, '_last', non_linearity)
        self.adaptive_pooling = nn.AdaptiveAvgPool2d(output_size)
        self.feature.add_module('adaptive_pooling2D', self.adaptive_pooling)

        # Compute the number of pixels (where idx is not -1 in the index matrix) of the last features
        self.n_pixels = torch.prod(torch.tensor(output_size))
        self.logger.info('num pixels after last pooling : {}'.format(self.n_pixels))

        self.initialize_weights(self.modules(), method=initialization)
        self.freeze_weights(self.feature, freeze=freeze)

    def forward(self, x: torch.Tensor, **kwargs):
        return self.feature(x)


class ResNetAttentionIndexed(_BaseModule):
    """
    ResNet like Network based on https://arxiv.org/abs/1603.05027, CIFAR version with full pre-activation,
    augmented with attention (see backbone definition :
    https://www.scitepress.org/Link.aspx?doi=10.5220/0010297405340544) and implemented with indexedconv.
    """
    def __init__(self, net_parameters_dic):
        """
        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        """
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.ResNetAttentionIndexed')

        index_matrix0, camera_layout = get_camera_layout_from_geom(net_parameters_dic['camera_geometry'])

        num_layers = net_parameters_dic['num_layers']
        num_channels = [net_parameters_dic['num_channels']]
        num_channels.extend(net_parameters_dic['block_features'])
        attention = net_parameters_dic['attention_layer']
        non_linearity = net_parameters_dic['non_linearity']
        normalization = net_parameters_dic.get('normalization', None)
        initialization = net_parameters_dic.get('initialization', 'kaiming')
        freeze = net_parameters_dic.get('freeze', False)
        self.num_features = num_channels[-1]

        # Check normalization and activation and convert to tuple if necessary
        normalization = self.check_normalization(normalization)
        non_linearity = self.check_activation(non_linearity)

        # ResNet backbone
        self.feature = nn.Sequential()

        # Layer 0
        indices_conv0 = cvutils.neighbours_extraction(index_matrix0, kernel_type=camera_layout)
        self.feature.add_module('cv0', IndexedConv(num_channels[0], 16, indices_conv0))
        self.add_activation(self.feature, '0', non_linearity)
        # Rearrange index matrix
        index_matrix1 = cvutils.pool_index_matrix(index_matrix0, stride=1, kernel_type=camera_layout)

        # blocks
        for i, (n_in, n_out) in enumerate(zip(num_channels[:-1], num_channels[1:])):
            if i == 0:
                for n in range(1, num_layers + 1):
                    pre_activation = False if n == 1 else True

                    layer = _ResidualLayerIndexed(n_out, n_out, index_matrix1, pre_activation=pre_activation,
                                                  normalization=normalization, non_linearity=non_linearity)
                    self.feature.add_module('block' + str(i) + '_layer' + str(n), layer)
            else:
                for n in range(1, num_layers + 1):
                    in_features = n_in if n == 1 else n_out
                    downsample = True if n == 1 else False

                    layer = _ResidualLayerIndexed(in_features, n_out, index_matrix1, downsample=downsample, 
                                                    normalization=normalization, non_linearity=non_linearity)
                    if n == 1: index_matrix1 = layer.pooled_matrix 
                    self.feature.add_module('block' + str(i) + '_layer' + str(n), layer)
            if attention is not None:
                self.feature.add_module('attention_block' + str(i), attention[0](n_out, **attention[1]))

        self.add_activation(self.feature, '_last', non_linearity)

        # Compute the number of pixels (where idx is not -1 in the index matrix) of the last features
        self.n_pixels = int(torch.sum(torch.ge(index_matrix1[0, 0], 0)).data)
        self.logger.debug('num pixels after last pooling : {}'.format(self.n_pixels))

        self.initialize_weights(self.modules(), method=initialization)
        self.freeze_weights(self.feature, freeze=freeze)

    def forward(self, x: torch.Tensor, **kwargs):
        return self.feature(x)


class GammaPhysNet(_BaseModule):
    """
        Gamma-PhysNet with ResNet
        Please cite and see details: https://www.scitepress.org/Link.aspx?doi=10.5220/0010297405340544
    """

    def __init__(self, net_parameters_dic):
        """

        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        """
        super(GammaPhysNet, self).__init__()
        self.logger = logging.getLogger(__name__ + '.GammaPhysNet')

        fc_width = net_parameters_dic['fc_width']
        non_linearity = net_parameters_dic['non_linearity']
        normalization = net_parameters_dic.get('normalization', None)
        last_bias_init = net_parameters_dic['last_bias_init']
        self.non_linearity = non_linearity() if isinstance(non_linearity, type) else non_linearity[0](**non_linearity[1])

        num_class = net_parameters_dic['targets']['class'] if 'class' in net_parameters_dic['targets'].keys() else 0
        regressor = {t: net_parameters_dic['targets'][t] for t in net_parameters_dic['targets'].keys() if t != 'class'}
        if len(regressor) == 0:
            regressor = None

        # Check normalization and activation and convert to tuple if necessary
        normalization = self.check_normalization(normalization)
        non_linearity = self.check_activation(non_linearity)

        # Backbone
        self.feature = net_parameters_dic['backbone']['model'](net_parameters_dic['backbone']['parameters'])

        # Multitasking block
        if regressor is not None:
            if 'energy' in regressor:
                self.energy = nn.Sequential()
                self.energy.add_module('en_layer1', nn.Linear(self.feature.num_features, fc_width))
                self.add_activation(self.energy, non_linearity[0].__name__ + '1', non_linearity)
                self.energy.add_module('en_out', nn.Linear(fc_width, regressor['energy']))
                if last_bias_init is not None and 'energy' in last_bias_init:
                    self.energy.en_out.bias = nn.Parameter(torch.tensor(last_bias_init['energy']))
            else:
                self.energy = None
            if 'impact' in regressor or 'direction' in regressor:
                self.fusion = nn.Linear(self.feature.n_pixels * self.feature.num_features, fc_width)
                if 'impact' in regressor:
                    self.impact = nn.Linear(fc_width, regressor['impact'])
                    if last_bias_init is not None and 'impact' in last_bias_init:
                        self.impact.bias = nn.Parameter(torch.tensor(last_bias_init['impact']))
                else:
                    self.impact = None
                if 'direction' in regressor:
                    self.direction = nn.Linear(fc_width, regressor['direction'])
                    if last_bias_init is not None and 'direction' in last_bias_init:
                        self.direction.bias = nn.Parameter(torch.tensor(last_bias_init['direction']))
                else:
                    self.direction = None
            else:
                self.fusion = None
        else:
            self.energy = None
            self.fusion = None
            self.direction = None
            self.impact = None
        if num_class > 0:
            self.classifier = nn.Linear(self.feature.n_pixels * self.feature.num_features, num_class)
            if last_bias_init is not None and 'class' in last_bias_init:
                self.classifier.bias = nn.Parameter(torch.tensor(last_bias_init['class']))
        else:
            self.classifier = None

    def forward(self, images: torch.Tensor, **kwargs):
        out = self.feature(images)
        out = torch.flatten(out, start_dim=2)
        out_e = torch.mean(out, 2)  # Global average pooling
        out = out.view(out.size(0), -1)
        out_tot = {}
        if self.energy is not None:
            out_tot['energy'] = self.energy(out_e)
        if self.fusion is not None:
            out_f = self.non_linearity(self.fusion(out))
            if self.impact is not None:
                out_tot['impact'] = self.impact(out_f)
            if self.direction is not None:
                out_tot['direction'] = self.direction(out_f)
        if self.classifier is not None:
            out_tot['class'] = self.classifier(out)
        return out_tot


class TorchConvNet(nn.Module):
    """
    Extracts backbone from torchvision convolutional models
    """
    def __init__(self, net_parameters_dic):
        super(TorchConvNet, self).__init__()
        self.logger = logging.getLogger(__name__ + '.TorchConvNet')

        pretrained = net_parameters_dic.get('pretrained', None)
        model = net_parameters_dic['model'](pretrained=pretrained)
        parameters = net_parameters_dic['parameters']
        num_channels = parameters['num_channels']
        avg_pool = parameters.get('output_size', (10, 10))
        dropout = parameters.get('dropout', False)  # TODO: include dropout

        if isinstance(model, ResNet):
            self.feature = torch.nn.Sequential(*list(model.children())[:-2])
            self.feature[0] = torch.nn.Conv2d(num_channels, self.feature[0].out_channels,
                                              kernel_size=self.feature[0].kernel_size,
                                              stride=self.feature[0].stride,
                                              padding=self.feature[0].padding,
                                              bias=False,
                                              )
            # To be consistent with all possible ResNet, we must consider 'conv1' from BasicBlock
            self.num_features = self.feature[-1][-1].conv1.out_channels

        elif isinstance(model, (EfficientNet, MobileNetV2, MobileNetV3)):
            self.feature = model.features
            self.feature[0][0] = torch.nn.Conv2d(num_channels, self.feature[0][0].out_channels,
                                                 kernel_size=self.feature[0][0].kernel_size,
                                                 stride=self.feature[0][0].stride,
                                                 padding=self.feature[0][0].padding,
                                                 bias=False
                                                 )
            self.num_features = self.feature[-1][0].out_channels

        else:
            raise ValueError('Unknown torch model')

        self.feature.add_module('avg_pool', torch.nn.AdaptiveAvgPool2d(avg_pool))

        # The following variables are mandatory to ensure compatibility with the DANN model.
        self.n_pixels = torch.prod(torch.tensor(avg_pool))
        self.n_latent_features = self.n_pixels * self.num_features

    def forward(self, images: torch.Tensor, **kwargs):
        return self.feature(images)


class TorchViT(nn.Module):
    """
    Extracts backbone from torchvision vision transformers (ViT) models
    """

    def __init__(self, net_parameters_dic):
        super(TorchViT, self).__init__()
        self.logger = logging.getLogger(__name__ + '.TorchViT')

        pretrained = net_parameters_dic['parameters'].get('pretrained', False)

        self.model = net_parameters_dic['model'](pretrained=pretrained)
        num_channels = net_parameters_dic['parameters']['num_channels']
        output_size = net_parameters_dic['parameters']['output_size']

        self.model.conv_proj = torch.nn.Conv2d(in_channels=num_channels,
                                               out_channels=self.model.conv_proj.out_channels,
                                               kernel_size=self.model.conv_proj.kernel_size,
                                               stride=self.model.conv_proj.stride,
                                               padding=self.model.conv_proj.padding,
                                               )

        self.latent_features = None

        def get_latent_features(m, input, output):
            self.latent_features = output[:, 0].unsqueeze(-1)

        self.model.encoder.register_forward_hook(get_latent_features)

        self.num_features = self.model.heads.head.in_features
        self.n_pixels = 1
        self.n_latent_features = self.n_pixels * self.num_features

    def forward(self, images: torch.Tensor, **kwargs):
        self.model(images)

        return self.latent_features
    

class GLNetIndexConv42(nn.Module):
    """
        Network with indexed convolutions and pooling.
        4 CL (after each conv layer, pooling is executed)
        2 FC
    """
    def __init__(self, net_parameters_dic):
        """
        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        """
        super(GLNetIndexConv42, self).__init__()
        self.logger = logging.getLogger(__name__ + '.GLNetIndexConv42')
        self.targets = net_parameters_dic['targets']

        index_matrix1, camera_layout = get_camera_layout_from_geom(net_parameters_dic['camera_geometry'])
        pooling_kernel = camera_layout

        # Channels
        num_outputs = sum(net_parameters_dic['targets'].values())
        self.num_channel = n1 = net_parameters_dic['num_channels']
        n_features = net_parameters_dic['n_features']
        n2 = n_features*2
        n3 = n2*2
        n4 = n3 * 2

        self.drop_rate = net_parameters_dic['drop_rate']

        # Layer 1 : IndexedConv
        indices_conv1 = cvutils.neighbours_extraction(index_matrix1,
                                                      kernel_type=camera_layout)
        # After the first convolution we need to reorganize the index matrix
        index_matrix1 = cvutils.pool_index_matrix(index_matrix1, kernel_type=pooling_kernel, stride=1)
        indices_pool1 = cvutils.neighbours_extraction(index_matrix1, kernel_type=pooling_kernel, stride=2)
        self.cv1 = IndexedConv(n1, n_features, indices_conv1)
        self.max_pool1 = IndexedMaxPool2d(indices_pool1)
        self.relu1 = nn.ReLU()
        self.bn1 = nn.BatchNorm1d(n_features)

        # Layer 2 : IndexedConv
        index_matrix2 = cvutils.pool_index_matrix(index_matrix1, kernel_type=pooling_kernel, stride=2)
        indices_conv2 = cvutils.neighbours_extraction(index_matrix2,
                                                      kernel_type=camera_layout)
        indices_pool2 = cvutils.neighbours_extraction(index_matrix2, kernel_type=pooling_kernel, stride=2)
        self.cv2 = IndexedConv(n_features, n2, indices_conv2)
        self.max_pool2 = IndexedMaxPool2d(indices_pool2)
        self.relu2 = nn.ReLU()
        self.bn2 = nn.BatchNorm1d(n2)

        # Layer 3 : IndexedConv
        index_matrix3 = cvutils.pool_index_matrix(index_matrix2, kernel_type=pooling_kernel, stride=2)
        indices_conv3 = cvutils.neighbours_extraction(index_matrix3,
                                                      kernel_type=camera_layout)
        indices_pool3 = cvutils.neighbours_extraction(index_matrix3, kernel_type=pooling_kernel, stride=2)
        self.cv3 = IndexedConv(n2, n3, indices_conv3)
        self.max_pool3 = IndexedMaxPool2d(indices_pool3)
        self.relu3 = nn.ReLU()
        self.bn3 = nn.BatchNorm1d(n3)

        # Layer 4 : IndexedConv
        index_matrix4 = cvutils.pool_index_matrix(index_matrix3, kernel_type=pooling_kernel, stride=2)
        indices_conv4 = cvutils.neighbours_extraction(index_matrix4,
                                                      kernel_type=camera_layout)
        indices_pool4 = cvutils.neighbours_extraction(index_matrix4, kernel_type=pooling_kernel, stride=2)
        self.cv4 = IndexedConv(n3, n4, indices_conv4)
        self.max_pool4 = IndexedMaxPool2d(indices_pool4)
        self.relu4 = nn.ReLU()
        self.bn4 = nn.BatchNorm1d(n4)

        index_matrix5 = cvutils.pool_index_matrix(index_matrix4, kernel_type=pooling_kernel, stride=2)

        # Compute the number of pixels (where idx is not -1 in the index matrix) of the last features
        n_pixels = int(torch.sum(torch.ge(index_matrix5[0, 0], 0)).data)
        self.logger.debug('num pixels after last conv : {}'.format(n_pixels))

        self.lin1 = nn.Linear(n_pixels*n4, (n_pixels*n4) // 2)
        self.relu5 = nn.ReLU()
        self.bn5 = nn.BatchNorm1d((n_pixels*n4) // 2)

        self.lin2 = nn.Linear((n_pixels*n4)//2, num_outputs)

        for m in self.modules():
            if isinstance(m, IndexedConv):
                nn.init.kaiming_uniform_(m.weight.data, mode='fan_out')

    def forward(self, images: torch.Tensor, **kwargs):
        drop = nn.Dropout(p=self.drop_rate)
        out_conv = []
        # In case of stereo, average convolutions output per telescope
        for i in range(int(images.shape[-2] / self.num_channel)):
            out = self.cv1(images[..., i*self.num_channel:(i+1)*self.num_channel, :])
            out = self.max_pool1(out)
            out = self.bn1(out)
            out = drop(self.relu1(out))
            out = self.cv2(out)
            out = self.max_pool2(out)
            out = self.bn2(out)
            out = drop(self.relu2(out))
            out = self.cv3(out)
            out = self.max_pool3(out)
            out = self.bn3(out)
            out = drop(self.relu3(out))
            out = self.cv4(out)
            out = self.max_pool4(out)
            out = self.bn4(out)
            out_conv.append(drop(self.relu4(out)))
        out = torch.stack(out_conv, 1)
        out = out.mean(1)
        out = out.view(out.size(0), -1)
        out = self.lin1(out)
        out = self.bn5(out)
        out = drop(self.relu5(out))

        out_linear2 = self.lin2(out)
        i = 0
        output = {}
        for t, v in self.targets.items():
            if t == 'class':
                output[t] = out_linear2[:, i:i + v]
            else:
                output[t] = out_linear2[:, i:i+v]
            i += v

        return output


class ResNet18MT(nn.Module):
    """
        ResNet18 for multitask IACT reco
    """
    def __init__(self, net_parameters_dic):
        """
        Parameters
        ----------
        net_parameters_dic (dict): a dictionary describing the parameters of the network
        """
        super(ResNet18MT, self).__init__()
        self.logger = logging.getLogger(__name__ + '.ResNet18MT')
        self.targets = net_parameters_dic['targets']

        self.model = resnet18(pretrained=False)

        # Channels
        num_outputs = sum(net_parameters_dic['targets'].values())
        num_channel = net_parameters_dic['num_channels']
        self.model.conv1 = torch.nn.Conv2d(num_channel, 64, kernel_size=(3, 3), padding=(1, 1))
        self.drop_rate = net_parameters_dic['drop_rate']
        self.model.fc = nn.Linear(512, 256)
        self.relu5 = nn.ReLU()
        self.bn5 = nn.BatchNorm1d(256)
        self.lin2 = nn.Linear(256, num_outputs)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight.data, mode='fan_out')

    def forward(self, images: torch.Tensor, **kwargs):
        drop = nn.Dropout(p=self.drop_rate)
        out = self.model(images)
        out = self.bn5(out)
        out = drop(self.relu5(out))

        out_linear2 = self.lin2(out)
        i = 0
        output = {}
        for t, v in self.targets.items():
            if t == 'class':
                output[t] = out_linear2[:, i:i + v]
            else:
                output[t] = out_linear2[:, i:i+v]
            i += v

        return output


class GammaDumbNet(nn.Module):
    """
    Very simple GammaPhysNet architecture that mimics the full GammaPhysNet architecture.
    """
    def __init__(self, net_parameters_dic, *args, **kwargs):
        super().__init__()

        num_channels = net_parameters_dic['block_features'][-1]

        # Encoder backbone
        self.feature = nn.Sequential()
        self.feature.add_module('f_conv1', nn.Conv2d(2, num_channels, 3, padding=1))
        self.feature.add_module('f_relu1', nn.ReLU())
        self.feature.add_module('f_pool1', nn.AdaptiveAvgPool2d((14, 14)))

        output_size = 14 * 14 * num_channels

        # Energy
        self.energy = nn.Sequential()
        self.energy.add_module('energy_fc1', nn.Linear(output_size, 1))

        # Impact
        self.impact = nn.Sequential()
        self.impact.add_module('impact_fc1', nn.Linear(output_size, 2))

        # Direction
        self.direction = nn.Sequential()
        self.direction.add_module('direction_fc1', nn.Linear(output_size, 2))

        # Classifier
        self.classifier = nn.Sequential()
        self.classifier.add_module('classifier_fc1', nn.Linear(output_size, 2))

    def forward(self, images: torch.Tensor, **kwargs):
        out = self.feature(images)
        out = out.view(out.size(0), -1)
        out_tot = {
            'energy': self.energy(out),
            'impact': self.impact(out),
            'direction': self.direction(out),
            'class': self.classifier(out)
        }

        return out_tot


class DANN(nn.Module):
    """
    Domain Adversarial Neural Network (DANN) based on the following article https://arxiv.org/abs/1505.07818.
    This entity consists of the addition of a domain classifier in parallel of the classification and regression tasks.
    Experimentally, convergence is observed only if the domain classifier contains at least 2 fully-connected layers.
    """
    def __init__(self, net_parameters_dic):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.DANN')

        # Implement the main task model
        main_task_parameters = net_parameters_dic['main_task']['parameters']
        self.main_task_model = net_parameters_dic['main_task']['model'](main_task_parameters)
        self.n_latent_features = self.main_task_model.feature.n_pixels * self.main_task_model.feature.num_features

        # Implement the domain classifier
        fc_features = net_parameters_dic.get('fc_features', 100)
        self.domain_classifier = nn.Sequential()
        self.domain_classifier.add_module('fc1_domain', LinearBlock(self.n_latent_features, fc_features))
        self.domain_classifier.add_module('fc2_domain', nn.Linear(fc_features, 2))
        self.domain_classifier.add_module('softmax', nn.Softmax(dim=-1))

        # Hooks allow to capture the data during a forward pass. In this context, it allows us to get the backbone
        # output
        self.feature_output = None

        def get_feature_output(module, input, output):
            self.feature_output = output

        self.main_task_model.feature.register_forward_hook(get_feature_output)

    def forward(self, x, **kwargs):
        lambda_p = kwargs.get('weight_grads', 1.)
        main_task_output = self.main_task_model(x, **kwargs)

        # The output must be a dictionary
        out_tot = main_task_output  # if isinstance(main_task_output, dict) else {}

        # The UNet encoder (for example) outputs a list, of which the last element is always the feature output
        feature_output = self.feature_output[-1] if isinstance(self.feature_output,
                                                               (tuple, list)) else self.feature_output

        # Reshape the latent representation from (batch_size, num_channels, (output_size))
        # to (batch_size, n_latent_features)
        feature_output = feature_output.flatten(start_dim=1)

        reverse_layer = GradientReverseLayer.apply
        out_tot['domain_class'] = self.domain_classifier(reverse_layer(feature_output, lambda_p))

        return out_tot


class GradientReverseLayer(torch.autograd.Function):
    """
    Gradient reverse layer defined in DANN. During the forward pass, the gradient remains unchanged, but is reversed
    during the backward pass. The context (ctx) is used to store the lambda_p variable, but can also be used to store
    any constant K.
    """
    @staticmethod
    def forward(ctx, x, K=1.):
        ctx.K = K
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.K, None


class GammaPhysNetPointing(GammaPhysNet):
    """
    GammaPhysNet with the addition of the pointing information.
    """
    def __init__(self, net_parameters_dic):
        super(GammaPhysNetPointing, self).__init__(net_parameters_dic)

        self.logger = logging.getLogger(__name__ + '.GammaPhysNetPointing')

        output_shape = self.feature.num_features * self.feature.n_pixels
        self.pointing_projection = nn.Sequential()
        self.pointing_projection.add_module('pointing_fc1', nn.Linear(2, output_shape))
        self.pointing_projection.add_module('pointing_bn1', nn.BatchNorm1d(output_shape))
        self.pointing_projection.add_module('pointing_relu1', nn.ReLU())

    def forward(self, images: torch.Tensor, pointing: torch.Tensor = None):
        out = self.feature(images)
        out = torch.flatten(out, start_dim=2)
        x_pointing_projected = self.pointing_projection(pointing).view(out.shape)
        out += x_pointing_projected

        out_e = torch.mean(out, 2)  # Global average pooling
        out = out.view(out.size(0), -1)
        out_tot = {}
        if self.energy is not None:
            out_tot['energy'] = self.energy(out_e)
        if self.fusion is not None:
            out_f = self.non_linearity(self.fusion(out))
            if self.impact is not None:
                out_tot['impact'] = self.impact(out_f)
            if self.direction is not None:
                out_tot['direction'] = self.direction(out_f)
        if self.classifier is not None:
            out_tot['class'] = self.classifier(out)
        return out_tot


class AutoEncoderClassifier(nn.Module):

    def __init__(self, net_parameters_dic):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.AutoEncoderClassifier')
        backbone_model = net_parameters_dic['backbone']['model']
        backbone_parameters = net_parameters_dic['backbone']['parameters']
        classifier_parameters = net_parameters_dic['classifier']['parameters']
        decoder_model = net_parameters_dic['decoder']['model']
        decoder_parameters = net_parameters_dic['decoder']['parameters']

        self.feature = backbone_model(backbone_parameters)
        self.classifier = nn.Linear(self.feature.n_latent_features, classifier_parameters['n_labels'])
        self.decoder = decoder_model(decoder_parameters)

    def forward(self, x, **kwargs):
        x = self.feature(x)

        output_decoder = self.decoder(x)[-1]

        output_class = x[-1].flatten(start_dim=1)
        output_class = self.classifier(output_class)

        return {'autoencoder': output_decoder, 'class': output_class}


class Classifier(nn.Module):

    def __init__(self, net_parameters_dic):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.Classifier')
        backbone_model = net_parameters_dic['backbone']['model']
        backbone_parameters = net_parameters_dic['backbone']['parameters']
        classifier_parameters = net_parameters_dic['classifier']['parameters']

        self.feature = backbone_model(backbone_parameters)
        self.classifier = nn.Sequential()

        if classifier_parameters.get('fc_features', False):
            self.classifier.add_module('fc1_features', nn.Linear(self.feature.n_latent_features,
                                                                 classifier_parameters.get('fc_features')))
            if classifier_parameters.get('dropout', False):
                self.classifier.add_module('dropout', torch.nn.Dropout(p=0.5))
            self.classifier.add_module('fc2_features', nn.Linear(classifier_parameters.get('fc_features'),
                                                                 classifier_parameters['n_labels']))
        else:
            self.classifier.add_module('fc1_features', nn.Linear(self.feature.n_latent_features,
                                                                 classifier_parameters['n_labels']))
        self.classifier.add_module('softmax', nn.Softmax(dim=-1))

        # Weight initialization
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight, mode='fan_out')

    def forward(self, x, **kwargs):
        x = self.feature(x)

        if isinstance(x, (tuple, list)):
            output_class = x[-1].flatten(start_dim=1)
        else:
            output_class = x.flatten(start_dim=1)
        output_class = self.classifier(output_class)

        return {'class': output_class}


class VAE(nn.Module):
    """
    Variational Auto-Encoder, inspired from https://github.com/milesial/Pytorch-UNet.
    """
    def __init__(self, net_parameters_dic):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.VAE')
        self.encoder = Encoder(net_parameters_dic)
        self.decoder = Decoder(net_parameters_dic)

        self.latent_dim = net_parameters_dic['latent_dim']
        self.encoding_dim = net_parameters_dic['latent_feature_size']
        self.num_features = net_parameters_dic['block_features'][-1]

        self.fc_mu = nn.Linear(self.encoder.n_latent_features, self.latent_dim)
        self.fc_var = nn.Linear(self.encoder.n_latent_features, self.latent_dim)
        self.decoder_input = nn.Linear(self.latent_dim, self.encoder.n_latent_features)

        self.mu = None
        self.log_var = None
        self.z = None

    def kl_divergence(self):
        return torch.mean(-0.5 * torch.sum(1 + self.log_var - self.mu ** 2 - self.log_var.exp(), dim=1), dim=0)

    def reparameterization(self):
        std = torch.exp(0.5 * self.log_var)
        eps = torch.randn_like(std)

        return eps * std + self.mu

    def encode(self, x, sequence=True):
        x = self.encoder(x)
        feature = x[-1].flatten(start_dim=1)

        self.mu = self.fc_mu(feature)
        self.log_var = self.fc_var(feature)

        return x if sequence else x[-1]

    def decode(self, x, sequence=True):
        y = self.decoder_input(self.z)
        y = y.view(-1, self.num_features, self.encoding_dim[0], self.encoding_dim[1])
        y = self.decoder([y] + x)

        return y if sequence else y[-1]

    def forward(self, x: torch.Tensor, **kwargs):
        feature = self.encode(x)
        self.z = self.reparameterization()
        y = self.decode(feature, sequence=False)

        return {'autoencoder': y}


class AutoEncoder(nn.Module):

    def __init__(self, net_parameters_dic):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.AutoEncoder')
        self.encoder = Encoder(net_parameters_dic)
        self.decoder = Decoder(net_parameters_dic)

    def forward(self, x: torch.Tensor, **kwargs):
        x = self.decoder(self.encoder(x))

        return {'autoencoder': x[-1]}


class UNet(nn.Module):

    def __init__(self, net_parameters_dic):
        super().__init__()
        self.logger = logging.getLogger(__name__ + '.UNet')
        self.encoder = Encoder(net_parameters_dic)
        self.decoder = Decoder(net_parameters_dic, unet=True)

    def forward(self, x: torch.Tensor, **kwargs):
        x = self.decoder(self.encoder(x))

        return {'autoencoder': x[-1]}


class Encoder(nn.Module):
    """
    Encoder entity for auto-encoder, UNet or VAE.
    """
    def __init__(self, net_parameters_dic):
        super().__init__()
        n_channels = net_parameters_dic['n_channels']  # Number of input channels
        latent_feature_size = net_parameters_dic['latent_feature_size']  # The expected shape of the latent space
        block_features = [n_channels] + net_parameters_dic['block_features']

        # To make auto-encoder, UNet or VAE compatible with DANN, the following arguments must be set.
        self.num_features = block_features[-1]
        self.n_pixels = torch.prod(torch.tensor(latent_feature_size))
        self.n_latent_features = self.n_pixels * self.num_features  # The number of coordinates in the latent space

        # Definition of the encoder. The first layer is a classic convolution block, and the last layer receives the
        # expected latent space shape defined in the network parameters dictionary.
        encoder = [ConvBlock(n_channels, block_features[1])]
        for i in range(2, len(block_features) - 1):
            encoder.append(ConvBlockDown(block_features[i - 1], block_features[i]))
        encoder.append(ConvBlockDown(block_features[-2], block_features[-1],
                                     latent_feature_size=latent_feature_size))
        self.encoder = nn.Sequential(*encoder)

    def forward(self, x, sequence=True):
        output = []
        for i, module in enumerate(self.encoder):
            output.append(module(x))
            x = output[i]

        return output if sequence else output[-1]


class Decoder(nn.Module):
    """
    Decoder entity for auto-encoder, UNet or VAE.
    """
    def __init__(self, net_parameters_dic, unet=False):
        super().__init__()
        n_channels = net_parameters_dic['n_channels']  # Number of input channels
        block_features = net_parameters_dic['block_features'][::-1] + [n_channels]

        # Definition of the decoder. The last layer receives the number of expected output channels defined in the
        # network parameters dictionary.
        decoder = []
        for i in range(1, len(block_features) - 1):
            decoder.append(ConvBlockUp(block_features[i - 1], block_features[i], unet=unet))
        decoder.append(ConvBlock(block_features[-2], n_channels))
        self.decoder = nn.Sequential(*decoder)

    def forward(self, x, sequence=True):
        x = x[::-1]
        output = []
        tmp = x[0]
        for i, module in enumerate(self.decoder[:-1]):
            output.append(module(x[i + 1], tmp))
            tmp = output[-1]
        output.append(self.decoder[-1](tmp))

        return output if sequence else output[-1]


class ConvBlockDown(nn.Module):
    """
    Basic convolution block for an encoder, inspired from https://github.com/milesial/Pytorch-UNet.
    """
    def __init__(self, in_channels, out_channels, latent_feature_size=None):
        super().__init__()

        if latent_feature_size is None:
            self.conv_block_down = nn.Sequential(
                nn.MaxPool2d(2),
                ConvBlock(in_channels, out_channels),
            )
        else:
            # Usually used as the last layer of the encoder
            self.conv_block_down = nn.Sequential(
                nn.AdaptiveAvgPool2d(latent_feature_size),
                ConvBlock(in_channels, out_channels),
            )

    def forward(self, x):
        return self.conv_block_down(x)


class ConvBlockUp(nn.Module):
    """
    Basic convolution block for a decoder, inspired from https://github.com/milesial/Pytorch-UNet.
    """
    def __init__(self, in_channels, out_channels, unet=False):
        super().__init__()
        self.unet = unet  # Allow connections between decoder and encoder
        mid_channels = in_channels + out_channels if self.unet else in_channels
        self.conv_block_up = nn.ConvTranspose2d(in_channels, in_channels, kernel_size=2, stride=2)
        self.conv_block = ConvBlock(mid_channels, out_channels)

    def forward(self, x1, x2):
        x2 = self.conv_block_up(x2)

        diff_y = x1.size()[2] - x2.size()[2]
        diff_x = x1.size()[3] - x2.size()[3]

        x2 = torch.nn.functional.pad(x2, [diff_x // 2, diff_x - diff_x // 2,
                                          diff_y // 2, diff_y - diff_y // 2])

        x = torch.cat([x2, x1], dim=1) if self.unet else x2

        return self.conv_block(x)


class ConvBlock(nn.Module):
    """
    Basic convolutional block, inspired from https://github.com/milesial/Pytorch-UNet.
    Consists in a three-layered elementary stage (convolution -> batch norm -> ReLU), assembled twice.
    The padding is set to '1' so the fixed kernel size of '3' has no edge effects.
    """
    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.conv_block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv_block(x)


class LinearBlock(nn.Module):
    """
    Basic linear block consisting in a three-layered elementary stage (fully-connected -> batch norm -> ReLU).
    """
    def __init__(self, in_features, out_features):
        super().__init__()

        self.linear_block = nn.Sequential(
            nn.Linear(in_features, out_features),
            nn.BatchNorm1d(out_features),
            nn.ReLU()
        )

    def forward(self, x):
        return self.linear_block(x)


class BaseMaskedAutoEncoder(nn.Module):
    """
    Implementation of
    https://openaccess.thecvf.com/content/CVPR2022/papers/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.pdf
    Widely inspired from https://github.com/facebookresearch/mae
    """
    def __init__(self, net_parameters_dic):
        super(BaseMaskedAutoEncoder, self).__init__()
        self.net_parameters_dic = net_parameters_dic
        self.add_token_list = net_parameters_dic['backbone']['parameters']['add_token_list']
        self.mask_ratio = net_parameters_dic['backbone']['parameters']['mask_ratio']
        self.add_pointing = net_parameters_dic['backbone']['parameters']['add_pointing']
        self.norm_pixel_loss = net_parameters_dic['norm_pixel_loss']

    def position_embedding(self, embed_dim):
        raise NotImplementedError()

    def initialize_mae(self):
        self._initialize_encoder()
        self._initialize_decoder()
        self._initialize_weights()

    def _initialize_encoder(self):
        encoder_embed_dim = self.net_parameters_dic['backbone']['parameters']['embed_dim']
        encoder_num_channels = self.net_parameters_dic['backbone']['parameters']['num_channels']
        encoder_blocks = self.net_parameters_dic['backbone']['parameters']['blocks']
        encoder_mlp_ratio = self.net_parameters_dic['backbone']['parameters']['mlp_ratio']
        encoder_heads = self.net_parameters_dic['backbone']['parameters']['heads']
        encoder_mlp_dim = encoder_embed_dim * encoder_mlp_ratio

        pos_emb, patch_size = self.position_embedding(encoder_embed_dim)
        # Even though it is fixed, set it as a parameter for PyTorch to set the proper device
        self.pos_embedding = nn.Parameter(pos_emb, requires_grad=False)
        self.pos_embedding.unsqueeze_(0)
        if self.add_token_list:
            self.additional_tokens = nn.Parameter(torch.zeros(1, len(self.add_token_list), encoder_embed_dim))
        if self.add_pointing:
            self.pointing_projection = nn.Linear(in_features=2, out_features=encoder_embed_dim)
        self.patch_projection = nn.Conv1d(in_channels=encoder_num_channels, out_channels=encoder_embed_dim,
                                          kernel_size=patch_size, stride=patch_size)
        self.encoder = nn.Sequential(OrderedDict(
            [('enc_block_{}'.format(i), EncoderBlock(num_heads=encoder_heads, hidden_dim=encoder_embed_dim,
                                                     mlp_dim=encoder_mlp_dim, dropout=0, attention_dropout=0,
                                                     norm_layer=nn.LayerNorm))
             for i in range(encoder_blocks)]
        )
        )
        self.encoder_norm = nn.LayerNorm(encoder_embed_dim)

    def _initialize_decoder(self):
        encoder_embed_dim = self.net_parameters_dic['backbone']['parameters']['embed_dim']
        encoder_num_channels = self.net_parameters_dic['backbone']['parameters']['num_channels']
        decoder_embed_dim = self.net_parameters_dic['decoder']['parameters']['embed_dim']
        decoder_blocks = self.net_parameters_dic['decoder']['parameters']['blocks']
        decoder_mlp_ratio = self.net_parameters_dic['decoder']['parameters']['mlp_ratio']
        decoder_heads = self.net_parameters_dic['decoder']['parameters']['heads']
        decoder_mlp_dim = decoder_embed_dim * decoder_mlp_ratio

        self.decoder_embedding = nn.Linear(encoder_embed_dim, decoder_embed_dim)
        self.mask_token = nn.Parameter(torch.zeros(1, 1, decoder_embed_dim))
        dec_pos_emb, patch_size = self.position_embedding(decoder_embed_dim)
        # Even though it is fixed, set it as a parameter for PyTorch to set the proper device
        self.decoder_pos_embedding = nn.Parameter(dec_pos_emb, requires_grad=False)
        self.decoder_pos_embedding.unsqueeze_(0)
        self.decoder = nn.Sequential(OrderedDict(
            [('enc_block_{}'.format(i), EncoderBlock(num_heads=decoder_heads, hidden_dim=decoder_embed_dim,
                                                     mlp_dim=decoder_mlp_dim, dropout=0, attention_dropout=0,
                                                     norm_layer=nn.LayerNorm))
             for i in range(decoder_blocks)])
        )
        self.decoder_norm = nn.LayerNorm(decoder_embed_dim)
        self.decoder_prediction = nn.Linear(decoder_embed_dim, patch_size * encoder_num_channels)

    def _initialize_weights(self):
        # init projection embedding like Linear instead of Conv
        nn.init.xavier_uniform_(self.patch_projection.weight.data)

        if self.add_token_list:
            nn.init.normal_(self.additional_tokens, std=0.02)
        nn.init.normal_(self.mask_token, std=0.02)

        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m):
        if isinstance(m, nn.Linear):
            # we use xavier_uniform following official JAX ViT:
            torch.nn.init.xavier_uniform_(m.weight)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def patchify(self, images: torch.Tensor) -> torch.Tensor:
        """
        images:  (N, C, image_length)
        x: (N, L, patch_size * C)
        """
        batch, channels, img_size = images.shape
        num_patches, patch_size = self.patch_indices.shape
        assert img_size % patch_size == 0, 'the image must be divisible by patch size'
        x = images.reshape(batch, channels, num_patches, patch_size)
        x = torch.einsum('ncmp->nmpc', x)
        x = torch.reshape(x, (batch, num_patches, channels * patch_size))
        return x

    def unpatchify(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (N, L, patch_size * C)
        images:  (N, C, image_length)
        """
        batch, seq_len, token_size = x.shape
        num_patches, patch_size = self.patch_indices.shape
        assert seq_len == num_patches
        assert token_size % patch_size == 0
        num_channels = token_size // patch_size
        x = x.reshape(batch, num_patches, patch_size, num_channels)
        x = torch.einsum('nmpc->ncmp', x)
        images = x.reshape(batch, num_channels, patch_size * num_patches)
        return images

    @staticmethod
    def apply_random_mask(tokens: torch.Tensor, mask_ratio: Union[float, torch.Tensor]) -> Tuple[torch.Tensor,
                                                                                                 torch.Tensor,
                                                                                                 torch.Tensor]:
        """
        Perform per-sample random masking by per-sample shuffling.
        Per-sample shuffling is done by argsort random noise.
        tokens: [N, L, D], sequence
        mask_ratio: the ratio of image to discard
        """
        batch, seq_len, token_size = tokens.shape
        len_keep = int(seq_len * (1 - mask_ratio))
        noise = torch.rand(batch, seq_len, device=tokens.device)
        # sort noise for each sample
        ids_shuffle = torch.argsort(noise, dim=1)  # ascend: small is kept, large is removed
        ids_restore = torch.argsort(ids_shuffle, dim=1)
        # keep the first subset
        ids_keep = ids_shuffle[:, :len_keep]
        masked_tokens = torch.gather(tokens, dim=1, index=ids_keep.unsqueeze(-1).repeat(1, 1, token_size))
        # generate the binary mask: 0 is kept, 1 is removed
        mask = torch.ones([batch, seq_len], device=tokens.device)
        mask[:, :len_keep] = 0
        # unshuffle to get the binary mask
        mask = torch.gather(mask, dim=1, index=ids_restore)
        return masked_tokens, mask, ids_restore

    def _unmask_tokens(self, tokens: torch.Tensor, ids_restore: torch.Tensor) -> torch.Tensor:
        """
        Unmask the tokens before feeding the decoder. The mask_token is shared across all the masked position
        tokens: tokens computed on the selected image patches by the encoder and projected in the decoder embedding size
        ids_restore: ids to restore token order as is before masking
        """
        batch, token_seq, token_size = tokens.shape
        seq_len = ids_restore.shape[1]
        # append mask tokens to sequence
        mask_tokens = self.mask_token.repeat(batch, seq_len - token_seq, 1)
        unmasked_tokens = torch.cat([tokens, mask_tokens], dim=1)
        # unshuffle
        unmasked_tokens = torch.gather(unmasked_tokens, dim=1, index=ids_restore.unsqueeze(-1).repeat(1, 1, token_size))
        return unmasked_tokens

    def forward_encoder(self, images: torch.Tensor, pointing: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor,
                                                                                            torch.Tensor]:
        # embed patches
        x = self.patch_projection(images)
        x = x.transpose(1, 2)
        tot_add_token_len = len(self.add_token_list) + 1 if self.add_pointing else len(self.add_token_list)
        # position embedding
        x = x + self.pos_embedding[:, tot_add_token_len:, :]
        # random masking
        x, mask, ids_restore = self.apply_random_mask(x, self.mask_ratio)
        # append additional tokens
        if self.add_token_list:
            add_tokens = self.additional_tokens + self.pos_embedding[:, :len(self.add_token_list), :]
            add_tokens = add_tokens.expand(x.shape[0], -1, -1)
            x = torch.cat((add_tokens, x), dim=1)
        # append telescope pointing token
        if self.add_pointing:
            assert pointing is not None
            point_token = self.pointing_projection(pointing.unsqueeze(1))
            point_token = point_token + self.pos_embedding[:, len(self.add_token_list):len(self.add_token_list)+1, :]
            x = torch.cat((point_token, x), dim=1)
        # transformer encoder
        x = self.encoder(x)
        x = self.encoder_norm(x)
        return x, mask, ids_restore

    def forward_decoder(self, tokens: torch.Tensor, ids_restore: torch.Tensor) -> torch.Tensor:
        # embed tokens
        x = self.decoder_embedding(tokens)
        # unmask tokens
        tot_add_token_len = len(self.add_token_list) + 1 if self.add_pointing else len(self.add_token_list)
        x_image = self._unmask_tokens(x[:, tot_add_token_len:, :], ids_restore)
        # append additional tokens
        x = torch.cat([x[:, :tot_add_token_len], x_image], dim=1)
        # add pos embedding
        x = x + self.decoder_pos_embedding
        # transformer decoder
        x = self.decoder(x)
        x = self.decoder_norm(x)
        # predict pixels
        x = self.decoder_prediction(x)
        # remove additional tokens
        if self.add_pointing:
            x = x[:, len(self.add_token_list)+1:, :]
        else:
            x = x[:, len(self.add_token_list):, :]
        return x

    def forward_loss(self, images: torch.Tensor, predictions: torch.Tensor, mask: torch.Tensor):
        """
        We compute the loss only for the patches that were discarded during the masking operation
        images: [N, C, D]
        predictions: [N, L, p*C]
        mask: [N, L], 0 is keep, 1 is remove,
        """
        targets = self.patchify(images)
        if self.norm_pixel_loss:
            # normalize the input pixels per module
            mean = targets.mean(dim=-1, keepdim=True)
            var = targets.var(dim=-1, keepdim=True)
            targets = (targets - mean) / (var + 1e-6)**.5
        # loss per patch
        loss = (predictions - targets)**2
        loss = loss.mean(dim=-1)
        # keep only masked patches
        loss = (loss * mask).sum() / mask.sum()
        return loss

    def forward(self, images, pointing=None):
        latent_tokens, mask, ids_restore = self.forward_encoder(images, pointing)
        predictions = self.forward_decoder(latent_tokens, ids_restore)
        loss = self.forward_loss(images, predictions, mask)
        return loss


class ImageMaskedAutoEncoder(BaseMaskedAutoEncoder):
    def __init__(self, net_parameters_dic):
        super(ImageMaskedAutoEncoder, self).__init__(net_parameters_dic)

        image_size = net_parameters_dic['backbone']['parameters']['image_size']
        self.patch_size = net_parameters_dic['backbone']['parameters']['patch_size']
        self.patch_indices, self.grid = get_patch_indices_and_grid(image_size, self.patch_size)

        self.initialize_mae()

    def position_embedding(self, embed_dim):
        pos_emb = get_2d_sincos_pos_embedding_from_grid(
            self.grid,
            embed_dim,
            self.add_token_list,
            self.add_pointing
        )

        return pos_emb, self.patch_size * self.patch_size


class LSTMaskedAutoEncoder(BaseMaskedAutoEncoder):
    def __init__(self, net_parameters_dic):
        super(LSTMaskedAutoEncoder, self).__init__(net_parameters_dic)

        geom = net_parameters_dic['backbone']['parameters']['camera_geometry']
        self.patch_indices, self.patch_centroids = get_patch_indices_and_centroids_from_geometry(geom)
        self.patch_size = self.patch_indices.shape[-1]

        self.initialize_mae()

    def position_embedding(self, embed_dim):
        pos_emb = get_2d_sincos_pos_embedding_from_patch_centroids(
            self.patch_centroids,
            embed_dim,
            self.add_token_list,
            self.add_pointing
        )

        return pos_emb, self.patch_size


class GammaPhysNetPrime(LSTMaskedAutoEncoder):
    """
    Implementation of
    https://openaccess.thecvf.com/content/CVPR2022/papers/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.pdf
    Widely inspired from https://github.com/facebookresearch/mae
    for LST
    """
    def __init__(self, net_parameters_dic: dict):
        super(GammaPhysNetPrime, self).__init__(net_parameters_dic)
        encoder_embed_dim = net_parameters_dic['backbone']['parameters']['embed_dim']
        encoder_weights = net_parameters_dic['backbone']['parameters'].get('weights', None)
        encoder_weights = get_torch_weights_from_lightning_checkpoint(encoder_weights)
        freeze_weights = net_parameters_dic['backbone']['parameters'].get('freeze_weights', False)

        # --------------------------------------------------------------------------------------------------------------
        # Decoder
        # We create one linear layer by task, predicting directly from the corresponding tokens
        self.targets = net_parameters_dic['targets'].keys()
        for t, output_size in net_parameters_dic['targets'].items():
            self.add_module(t, nn.Linear(encoder_embed_dim, output_size))

        self.decoder = None
        self.decoder_pos_embedding = None
        self.decoder_embedding = None
        self.decoder_prediction = None
        self.mask_token = None
        self.decoder_norm = None
        # --------------------------------------------------------------------------------------------------------------

        self.load_pretrained_weights(encoder_weights)
        if freeze_weights:
            self.freeze_pretrained_weights(encoder_weights)

    def load_pretrained_weights(self, weights: dict):
        if weights is not None:
            for name, param in self.named_parameters():
                if name in weights.keys() and not param.requires_grad:
                    weights.pop(name)
            self.load_state_dict(weights, strict=False)

    def freeze_pretrained_weights(self, weights: dict):
        if weights is not None:
            for k, v in self.named_parameters():
                if k in weights.keys():
                    v.requires_grad = False

    def forward_predictor(self, tokens: torch.Tensor, ids_restore: torch.Tensor) -> dict:
        # get prediction tokens
        pointing_token = 1 if self.add_pointing else 0
        tot_add_token_len = len(self.add_token_list) + pointing_token
        prediction_tokens = tokens[:, pointing_token:tot_add_token_len]
        output = {t: self._modules[t](prediction_tokens[:, i]) for i, t in enumerate(self.targets)}
        return output

    def forward(self, images, pointing=None) -> dict:
        latent_tokens, mask, ids_restore = self.forward_encoder(images, pointing)
        predictions = self.forward_predictor(latent_tokens, ids_restore)
        return predictions

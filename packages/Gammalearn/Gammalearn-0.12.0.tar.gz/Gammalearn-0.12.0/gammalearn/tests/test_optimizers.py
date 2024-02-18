import unittest
import torch
from torch.optim import AdamW
from ctapipe.instrument import CameraGeometry
from gammalearn.optimizers import prime_optimizer
from gammalearn.data.nets import GammaPhysNetPrime

import collections


class TestOptimizers(unittest.TestCase):

    def setUp(self) -> None:
        optimizer_parameters = {
                'optimizer': AdamW,
                'optimizer_parameters': {
                    'lr': 1.5e-4,
                    'weight_decay': 0.05,
                    'betas': (0.9, 0.95),
                },
                'layer_decay': 0.75
        }
        targets = collections.OrderedDict({
            'energy': {
                'output_shape': 1,
            },
            'impact': {
                'output_shape': 2,
            },
            'direction': {
                'output_shape': 2,
            },
            'class': {
                'output_shape': 2,
            },
        })
        net_parameters_dic = {
                'backbone': {
                    'parameters': {
                        'num_channels': 2,
                        'blocks': 8,
                        'embed_dim': 512,
                        'mlp_ratio': 4,
                        'heads': 16,
                        'add_token_list': list(targets.keys()),
                        'mask_ratio': 0.75,
                        'add_pointing': True,
                        'weights': None,
                        'freeze_weights': False,
                        'camera_geometry': CameraGeometry.from_name('LSTCam')
                    }
                },
                'targets': {k: v.get('output_shape', 0) for k, v in targets.items()},
                'decoder': {
                    'parameters': {
                        'blocks': 2,
                        'embed_dim': 512,
                        'mlp_ratio': 4,
                        'heads': 16,
                    }
                },
                'norm_pixel_loss': False,
            }

        self.model = GammaPhysNetPrime(net_parameters_dic)
        self.optimizer = prime_optimizer(self.model, optimizer_parameters)

    def test_prime_optimizer(self):
        optim_params = []
        for group in self.optimizer.param_groups:
            optim_params.extend(group['params'])
        for p in self.model.parameters():
            if p.requires_grad:
                assert p in set(optim_params)

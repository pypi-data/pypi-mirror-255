import unittest
import gammalearn.data.nets as nets
import torch
import torchvision.models as models
from ctapipe.instrument import CameraGeometry


class TestNets(unittest.TestCase):

    def setUp(self) -> None:
        self.input = torch.rand(10, 2, 55, 55)

        self.resnet18 = {
            'model': models.resnet18,
            'parameters':
                {
                    'output_size': (7, 7),
                    'num_channels': 2
                }
        }
        self.mobilenet_v2 = {
            'model': models.mobilenet_v2,
            'parameters':
                {
                    'output_size': (9, 9),
                    'num_channels': 2
                }
        }
        self.mobilenet_v3 = {
            'model': models.mobilenet_v3_large,
            'parameters':
                {
                    'output_size': (9, 9),
                    'num_channels': 2
                }
        }
        self.efficient_net = {
            'model': models.efficientnet_b7,
            'parameters':
                {
                    'output_size': (9, 9),
                    'num_channels': 2
                }
        }

        self.mae = {
            'model': nets.LSTMaskedAutoEncoder,
            'parameters': {
                'backbone': {
                    'parameters': {
                        'num_channels': 2,
                        'blocks': 24,
                        'embed_dim': 1024,
                        'mlp_ratio': 4,
                        'heads': 16,
                        'add_token_list': [],
                        'mask_ratio': 0.75,
                        'camera_geometry': CameraGeometry.from_name('LSTCam'),
                        'add_pointing': True,
                    }
                },
                'decoder': {
                    'parameters': {
                        'blocks': 8,
                        'embed_dim': 512,
                        'mlp_ratio': 4,
                        'heads': 16,
                    }
                },
                'norm_pixel_loss': False
            }
        }

    def test_resnet18(self):
        net = nets.TorchConvNet(self.resnet18)
        output = net(self.input)
        assert net.num_features == 512
        assert output.shape[1] == 512
        assert output.shape[2:] == self.resnet18['parameters']['output_size']
        assert net.n_pixels == torch.prod(torch.tensor(output.shape[2:]))

    def test_mobilenet_v2(self):
        net = nets.TorchConvNet(self.mobilenet_v2)
        output = net(self.input)
        assert net.num_features == 1280
        assert output.shape[1] == 1280
        assert output.shape[2:] == self.mobilenet_v2['parameters']['output_size']
        assert net.n_pixels == torch.prod(torch.tensor(output.shape[2:]))

    def test_mobilenet_v3(self):
        net = nets.TorchConvNet(self.mobilenet_v3)
        output = net(self.input)
        assert net.num_features == 960
        assert output.shape[1] == 960
        assert output.shape[2:] == self.mobilenet_v3['parameters']['output_size']
        assert net.n_pixels == torch.prod(torch.tensor(output.shape[2:]))

    def test_efficient_net(self):
        net = nets.TorchConvNet(self.efficient_net)
        output = net(self.input)
        assert net.num_features == 2560
        assert output.shape[1] == 2560
        assert output.shape[2:] == self.efficient_net['parameters']['output_size']
        assert net.n_pixels == torch.prod(torch.tensor(output.shape[2:]))

    def test_mae(self):
        net = self.mae['model'](self.mae['parameters'])
        images = torch.rand(2, 2, 1855)
        pointing = torch.rand(2, 2)
        patches = net.patchify(images)
        assert patches.ndim == 3
        assert torch.all(net.unpatchify(patches) == images)

        ratio = torch.tensor(0.75)
        tokens = net.patch_projection(images)
        tokens = tokens.transpose(1, 2)
        masked_tokens, mask, ids_restore = net.apply_random_mask(tokens, ratio)
        assert masked_tokens.ndim == 3
        masked_patches_ratio = torch.count_nonzero(mask, dim=1) / mask.shape[1]
        assert torch.allclose(masked_patches_ratio, ratio, atol=0.01)

        enc_tokens, mask, ids_restore = net.forward_encoder(images, pointing)
        enc_tokens_dec = net.decoder_embedding(enc_tokens)
        unmasked_tokens = net._unmask_tokens(enc_tokens_dec, ids_restore)
        assert unmasked_tokens.shape == (2, 265, 512)

        predictions = net.forward_decoder(enc_tokens, ids_restore)
        image_patches = net.patchify(images)
        assert predictions.shape == image_patches.shape
        unpatched_pred = net.unpatchify(predictions)
        assert unpatched_pred.shape == images.shape

        loss = net(images, pointing)


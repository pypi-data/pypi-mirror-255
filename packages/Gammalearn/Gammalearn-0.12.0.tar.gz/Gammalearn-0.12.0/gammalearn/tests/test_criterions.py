import unittest
import torch
from pytorch_lightning import Trainer, LightningModule

from gammalearn.criterions import one_hot
import gammalearn.criterions as criterions
import gammalearn.constants as csts


class TestModule(LightningModule):

    def __init__(self):
        super().__init__()

    def train_dataloader(self):
        pass

    def training_step(self):
        pass

    def configure_optimizers(self):
        pass


class TestCriterions(unittest.TestCase):

    def setUp(self) -> None:
        self.labels = torch.tensor([0, 1, 1, 0, 1, 0, 0, 1], dtype=torch.long)
        self.onehot = torch.tensor([[1, 0],
                                    [0, 1],
                                    [0, 1],
                                    [1, 0],
                                    [0, 1],
                                    [1, 0],
                                    [1, 0],
                                    [0, 1]], dtype=torch.long)
        self.targets = {
            'energy': {
                'output_shape': 1,
                'loss': torch.nn.L1Loss(reduction='none'),
                'loss_weight': 1,
                'metrics': {
                    # 'functions': ,
                },
                'mt_balancing': True
            },
            'impact': {
                'output_shape': 2,
                'loss': torch.nn.L1Loss(reduction='none'),
                'loss_weight': 1,
                'metrics': {},
                'mt_balancing': True
            },
            'class': {
                'output_shape': 2,
                'label_shape': 1,
                'loss': torch.nn.CrossEntropyLoss(),
                'loss_weight': 1,
                'metrics': {},
                'mt_balancing': True
            },
        }
        self.batch_size = 1
        self.particle_dict = {0: 1, 1: 2, 101: 0}
        self.loss_options_masked = {
            'conditional': True,
            'gamma_class': self.particle_dict[csts.GAMMA_ID],
        }
        self.loss_options_masked_miss_gamma = {
            'conditional': True,
        }
        self.loss_options_not_masked = {
            'conditional': False,
            'gamma_class': self.particle_dict[csts.GAMMA_ID],
        }
        self.outputs_loss = {
            'energy': torch.tensor([0.1, 0.2, 0.1, 0.3, 0.6]).unsqueeze(1),
            'impact': torch.tensor([[1.1, 1.5, 1.9, 0.7, 0.8],
                                    [0.3, 0.6, 2.1, 2.2, 0.1]]).transpose(0, 1),
            'class': torch.log(torch.tensor([[0.7, 0.6, 0.3, 0.8, .2],
                                             [0.3, 0.4, 0.7, 0.2, 0.8]])).transpose(0, 1)
        }
        self.labels_loss = {
            'energy': torch.tensor([0.2, 0.1, 0.05, 0.5, 0.1]).unsqueeze(1),
            'impact': torch.tensor([[1.3, 0.5, 0.9, 1.7, 0.9],
                                    [0.2, 0.9, 2.0, 2.1, 0.3]]).transpose(0, 1),
            'class': torch.tensor([1, 0, 0, 1, 1])
        }
        self.true_losses_masked = [torch.tensor(0.8/3), torch.tensor(1.7/6),
                                   - (torch.log(torch.tensor(0.3)) +
                                      torch.log(torch.tensor(0.6)) +
                                      torch.log(torch.tensor(0.3)) +
                                      torch.log(torch.tensor(0.2)) +
                                      torch.log(torch.tensor(0.8))).squeeze() / 5
                                   ]

        self.true_losses_not_masked = [torch.tensor(0.95/5), torch.tensor(5.1/10),
                                       - (torch.log(torch.tensor(0.3)) +
                                          torch.log(torch.tensor(0.6)) +
                                          torch.log(torch.tensor(0.3)) +
                                          torch.log(torch.tensor(0.2)) +
                                          torch.log(torch.tensor(0.8))).squeeze() / 5
                                       ]

        self.module = TestModule()        
        trainer = Trainer(gpus=0, max_epochs=0)
        trainer.fit(self.module)

    def test_onehot(self):
        torch.allclose(self.onehot.float(),
                       one_hot(self.labels, num_classes=2).float())

    def test_loss_balancing_masked(self):
        loss_func = criterions.LossComputing(self.targets, **self.loss_options_masked)
        loss_func_mt = criterions.UncertaintyWeighting(self.targets)
        loss, _ = loss_func.compute_loss(self.outputs_loss, self.labels_loss, self.module)
        loss = loss_func_mt(loss, self.module)
        loss = [v for k, v in loss.items()]
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_masked))

    def test_loss_balancing_not_masked(self):
        loss_func = criterions.LossComputing(self.targets, **self.loss_options_not_masked)
        loss_func_mt = criterions.UncertaintyWeighting(self.targets)
        loss, _ = loss_func.compute_loss(self.outputs_loss, self.labels_loss, self.module)
        loss = loss_func_mt(loss, self.module)
        loss = [v for k, v in loss.items()]
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_not_masked))

    def test_uncertainty_loss_masked(self):
        loss_func = criterions.LossComputing(self.targets, **self.loss_options_masked)
        loss_func_mt = criterions.UncertaintyWeighting(self.targets)
        loss, _ = loss_func.compute_loss(self.outputs_loss, self.labels_loss, self.module)
        loss = loss_func_mt(loss, self.module)
        loss = [v for k, v in loss.items()]
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_masked))

    def test_uncertainty_loss_not_masked(self):
        loss_func = criterions.LossComputing(self.targets, **self.loss_options_not_masked)
        loss_func_mt = criterions.UncertaintyWeighting(self.targets)
        loss, _ = loss_func.compute_loss(self.outputs_loss, self.labels_loss, self.module)
        loss = loss_func_mt(loss, self.module)
        loss = [v for k, v in loss.items()]
        torch.allclose(torch.tensor(loss), torch.tensor(self.true_losses_not_masked))


if __name__ == '__main__':
    unittest.main()

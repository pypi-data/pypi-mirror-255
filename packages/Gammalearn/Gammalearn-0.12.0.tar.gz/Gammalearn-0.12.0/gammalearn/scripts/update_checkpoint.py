import torch
import argparse
import importlib
import pytorch_lightning as pl
from gammalearn.experiment_runner import Experiment, LitGLearnModule
from gammalearn.data_handlers import GLearnDataModule

def update_checkpoint(checkpoint, experiment, output_file):

    experiment.batch_size = 1
    experiment.train_files_max_number = 1
    experiment.test_files_max_number = 1
    experiment.gpus = 0
    lightning_module = LitGLearnModule(experiment)
    data_module = GLearnDataModule(experiment)
    data_module.setup()

    # Create an instance of your LightningModule
    model = lightning_module
    model.load_state_dict(checkpoint['state_dict'])

    trainer = pl.Trainer(max_epochs=0)  

    # Fit the model
    trainer.fit(model, data_module.train_dataloader())
    trainer.save_checkpoint(output_file)


def main():
    parser = argparse.ArgumentParser(description="Produce a new PyTorch checkpoint with the settings from a settings file and the weights from an existing checkpoint."\
                                     "Example: python checkpoint_to_weights.py -i last.ckpt -s settings.py -o new.ckpt"
                                     )
    parser.add_argument("-i", "--input", required=True, help="Path to the input checkpoint file")
    parser.add_argument("-s", "--settings", required=True, help="Path to the settings file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output weights file")

    args = parser.parse_args()
    
    spec = importlib.util.spec_from_file_location("settings", args.settings)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    experiment = Experiment(settings)
    
    checkpoint = torch.load(args.input, map_location=torch.device('cpu'))
    
    update_checkpoint(checkpoint, experiment, args.output)


if __name__ == "__main__":
    main()

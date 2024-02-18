from transformers import DeiTModel, DeiTConfig
import numpy as np
import torch
import torch.nn as nn
import torchvision
import lightning as l
from pyniche.models.mlp import NicheMLP


class NicheDeiTModule(l.LightningModule):
    def __init__(
        self,
        pretrained: str,  # facebook/deit-base-distilled-patch16-224
        lr: float = 1e-4,
        mlp_hidden_features: int = 256,
        mlp_n_layers: int = 3,
        mlp_out_features: int = 11,
        freeze_ext: bool = True,
        batch: int = -1,  # for logging only
    ):
        super().__init__()
        self.save_hyperparameters()
        self.pretrained = pretrained
        self.freeze_ext = freeze_ext
        self.lr = lr
        self.mlp_hidden_features = mlp_hidden_features
        self.mlp_n_layers = mlp_n_layers
        self.mlp_out_features = mlp_out_features
        self.batch = batch
        self.best_val_loss = np.inf
        # model configuration
        self.deit, self.mlp = self.configure_model()
        self.loss_func = nn.CrossEntropyLoss()
        # prepare for training
        self = self.float()
        self.example_input_array = torch.rand(1, 3, 224, 224)

    def forward(self, x):
        out = self.deit(x)
        out = self.mlp(out.pooler_output)
        return out

    # behavior before the training starts
    def on_fit_start(self):
        # print all trainable parameters
        print("--- NICHE MODULE MESSAGE ---")
        print("Trainable parameters:")
        for name, param in self.named_parameters():
            if param.requires_grad:
                print(name)
        # # log
        # self.logger.log_hyperparams(
        #     self.hparams,
        #     {"cross_entropy_loss": 9999}
        # )

    def on_fit_end(self):
        """
        log the best val_loss
        """
        best_val_loss = self.trainer.checkpoint_callback.best_model_score.item()
        # "hp_metric" is the default name for TensorBoardLogger
        self.logger.log_hyperparams(self.hparams, {"cross_entropy_loss": best_val_loss})

    def training_step(self, batch, batch_idx):
        x, y = self.extract_batch(batch)
        loss = self.loss_func(self(x), y)
        self.logger.experiment.add_scalar("Loss/Train", loss, self.global_step)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = self.extract_batch(batch)
        loss = self.loss_func(self(x), y)
        self.log("val_loss", loss)
        self.logger.experiment.add_scalar("Loss/Val", loss, self.global_step)
        return loss

    def test_step(self, batch, batch_idx):
        x, y = self.extract_batch(batch)
        loss = self.loss_func(self(x), y)
        return loss

    def predict_step(self, batch, batch_idx):
        x, y = self.extract_batch(batch)
        return self(x)  # return predictions

    def extract_batch(self, batch):
        x, y = batch["x"], batch["y"]
        x = x.float()
        y = y.squeeze(1).long()  # from (batch, 1) to (batch)
        return x, y

    def configure_optimizers(self):
        trainable_params = filter(lambda p: p.requires_grad, self.parameters())
        optimizer = torch.optim.Adam(trainable_params, lr=self.lr)
        return optimizer

    def configure_model(self):
        # config
        deit_config = DeiTConfig.from_pretrained(self.pretrained)
        deit_config.output_attentions = True
        # modify DeiT
        deit = DeiTModel(deit_config)
        layers = list(deit.children())
        in_features = layers[-1].dense.in_features
        deit.pooler.dense = nn.Identity()
        deit.pooler.activation = nn.Identity()
        # MLP
        mlp = NicheMLP(
            in_features=in_features,
            out_features=self.mlp_out_features,
            hidden_features=self.mlp_hidden_features,
            n_layers=self.mlp_n_layers,
        )
        # freeze the model
        for param in deit.parameters():
            param.requires_grad = not self.freeze_ext
        for param in mlp.parameters():
            param.requires_grad = True
        # return
        return deit, mlp

    def unfreeze_ext(self):
        for param in self.deit.parameters():
            param.requires_grad = True

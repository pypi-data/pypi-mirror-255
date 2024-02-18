# native imports
import os

# torch imports
import torch
import lightning as L
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger


class NicheTrainer:
    def __init__(self, device="cpu"):
        # core
        self.model = None  # lightning module
        self.data = None  # lightning data module
        self.trainer = None  # lightining trainer
        self.device = device  # cpu, cuda, or mps
        # outputs
        self.loggers = None  # lightning loggers
        self.callbacks = None  # lightning callbacks
        self.out = dict(
            {
                "dir": None,
                "best_loss": None,
                "best_path": None,
            }
        )

    def set_model(
        self,
        model_class: L.LightningModule,
        checkpoint=None,
        **kwargs,
    ):
        """
        parameters
        ---
        model_class: l.LightningModule
            the lightning module class, e.g., transformers.DetrModel

        other keyword arguments
        ---
        pretrained: str
            path to the pretrained model, e.g., facebook/detr-resnet-50
        checkpoint: str
            local path to the checkpoint, e.g., model.ckpt
        config: any
            model configuration, e.g., transformers.DetrConfig

        """
        if checkpoint:
            self.model = model_class.load_from_checkpoint(checkpoint, **kwargs)
            print(f"model loaded from {checkpoint}")
        else:
            # pretrained or config
            self.model = model_class(**kwargs)
        self.model.to(self.device)

    def set_data(
        self,
        dataclass: L.LightningDataModule,
        **kwargs,  # varied arguments for the dataclass
    ):
        self.data = dataclass(**kwargs)

    def set_out(
        self,
        dir_out: str,
    ):
        self.out["dir"] = dir_out
        if not os.path.exists(self.out["dir"]):
            os.makedirs(self.out["dir"])

    def fit(
        self,
        epochs: int = 100,
    ):
        self.loggers = get_logger(self.out["dir"])
        self.callbacks = get_checkpoint(self.out["dir"])
        self.trainer = L.Trainer(
            max_epochs=epochs,
            callbacks=self.callbacks,
            logger=self.loggers,
        )
        self.trainer.fit(self.model, self.data)

    def val(self):
        self.trainer = L.Trainer()
        out = self.trainer.validate(self.model, self.data)
        return out

    def predict(self, split="test"):
        """
        this will call model.predict_step()
        """
        self.trainer = L.Trainer()
        if split == "train":
            dataloader = self.data.train_dataloader()
        elif split == "val":
            dataloader = self.data.val_dataloader()
        elif split == "test":
            dataloader = self.data.test_dataloader()
        out = self.trainer.predict(self.model, dataloader)
        # out is a nested list (# of batches, batch_size)
        # flatten the list
        out = [item for sublist in out for item in sublist]
        return out

    def get_best_loss(
        self,
        rm_threshold: float = 1e5,
    ):
        self.out["best_loss"] = self.callbacks.best_model_score.item()
        self.out["best_path"] = self.callbacks.best_model_path
        if self.out["best_loss"] > rm_threshold:
            os.remove(self.out["best_path"])
        return self.out["best_loss"]

    def load_best_model(self):
        try:
            best_path = self.callbacks.best_model_score.item()
            self.model = self.model.load_from_checkpoint(best_path)
            self.model.to(self.device)
            print(f"model loaded from {best_path}")
        except Exception as e:
            print(e)


def get_logger(dir_out):
    # training configuration
    logger = TensorBoardLogger(
        save_dir=dir_out,
        name=".",  # will not create a new folder
        version=".",  # will not create a new folder
        log_graph=True,  # for model architecture visualization
        default_hp_metric=False,
    )  # output: save_dir/name/version/hparams.yaml
    return logger


def get_checkpoint(dir_out):
    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        dirpath=dir_out,
        mode="min",
        save_top_k=1,
        verbose=False,
        save_last=False,
        filename="model-{val_loss:.3f}",
    )
    return checkpoint_callback

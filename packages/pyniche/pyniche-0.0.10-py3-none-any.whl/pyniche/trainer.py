# native imports
from math import e
import os

# torch imports
import torch
import lightning as L
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger

# pyniche
from pyniche.data.yolo.API import YOLO_API
from pyniche.models.detection.yolo import NicheYOLO
from pyniche.evaluate import from_sv


class NicheTrainer:
    def __init__(self, device="cpu"):
        # core
        self.model = None  # lightning module instance
        self.modelclass = None  # lightning module class
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
        # special case for YOLO
        self.type = "lightning"  # "yolo" or "lightning"
        self.batch = None

    def set_model(
        self,
        modelclass,
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
            if YOLO,
                path to the model.pt, e.g., yolov8n.pt
            else,
                local path to the checkpoint, e.g., model.ckpt
        config: any
            model configuration, e.g., transformers.DetrConfig

        """
        self.modelclass = modelclass
        if "NicheYOLO" in str(modelclass):
            # YOLO model
            self.model = modelclass(checkpoint)
            self.type = "yolo"
        else:
            if checkpoint:
                self.model = modelclass.load_from_checkpoint(checkpoint, **kwargs)
                print(f"model loaded from {checkpoint}")
            else:
                # pretrained or config
                self.model = modelclass(**kwargs)
            self.model.to(self.device)

    def set_data(
        self,
        dataclass,  # L.LightningDataModule or path to yaml (yolo)
        batch: int = 32,
        n: int = None,  # number of images to be included in the train/val set
        k: int = 5,  # for train/val split
        **kwargs,  # varied arguments for the dataclass
    ):
        if self.type == "yolo":
            self.data = YOLO_API(root=dataclass)
            self.data.shuffle_train_val(n=n, k=k)
            self.data.save_yaml(classes=["cow"])  # assumed yaml is data.yaml
            self.batch = batch
        else:
            self.data = dataclass(
                batch=batch,
                n_train=n,
                k=k,
                **kwargs,
            )

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
        if self.type == "yolo":
            # ultralytics YOLO
            self.model.train(
                path_yaml=self.data.path_yaml(),
                name_task=self.out["dir"],
                batch=self.batch,
                epochs=epochs,
                device=self.device,
            )
        else:
            # lightning module
            self.loggers = get_logger(self.out["dir"])
            self.callbacks = get_checkpoint(self.out["dir"])
            self.trainer = L.Trainer(
                max_epochs=epochs,
                callbacks=self.callbacks,
                logger=self.loggers,
            )
            self.trainer.fit(self.model, self.data)
            self.set_best()
            self.load_best_model()

    def val(self):
        self.trainer = L.Trainer()
        out = self.trainer.validate(self.model, self.data)
        return out

    def evaluate_on_test(self):
        """
        return performance metrics on test set
        the metric is organized as a dictionary
        Example:
            {
                'map5095': 0.021785979618286846,
                'map50': 0.029330448337724434,
                'precision': 0.023825731790333562,
                'recall': 0.5,
                'f1': 0.045484080571799874,
                'n_all': 16,
                'n_fn': 35,
                'n_fp': 1434
            }
        """
        if self.type == "yolo":
            return self.model.evaluate(
                name_task=self.out["dir"],
                split="test",
                device=self.device,
            )
        else:
            # ligthning module
            # get data info
            obs = self.data.get_detections("test")
            # get predictions
            preds = self.predict("test")
            # output performance metrics
            return from_sv(preds, obs)

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

    def set_best(self):
        self.out["best_loss"] = self.callbacks.best_model_score.item()
        self.out["best_path"] = self.callbacks.best_model_path

    def get_best_loss(
        self,
        rm_threshold: float = 1e5,
    ):
        if self.out["best_loss"] > rm_threshold:
            os.remove(self.out["best_path"])
        return self.out["best_loss"]

    def get_best_path(self):
        return self.out["best_path"]

    def load_best_model(self):
        try:
            self.set_model(
                modelclass=self.modelclass,
                checkpoint=self.out["best_path"],
            )
            self.model.to(self.device)
            print("model loaded from %s" % self.out["best_path"])
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

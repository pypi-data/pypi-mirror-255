
# torch imports
import lightning as l
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import CSVLogger

class NicheViT(l.LightningModule):

    def __init__(
        self,
        loss,  # options: [MSE, MAE]
        optimizer,  # options: [Adam, SGD]
        lr,  # learning rate
    ):
        pass
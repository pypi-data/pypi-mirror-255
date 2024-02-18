import unittest
import niche_cv as nc
from niche_cv.detection.models.detr import Niche_Detr
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
# output
DIR_TEST = os.path.join(ROOT, "test")
DIR_OUT = os.path.join(DIR_TEST, "out")
# module
DIR_MODULE = os.path.join(ROOT, "niche_cv")
DIR_DATA = os.path.join(DIR_MODULE, "detection", "data", "balloon")


class TestDeTR(unittest.TestCase):
    def setUp(self):
        self.model = Niche_Detr(
            path_model="facebook/detr-resnet-50",
            dir_out=DIR_OUT,
            name_task="test",
            device="CUDA",
        )
        print("--- Finish setup ---")
        print(self.model)

    def test_train(self):
        self.model.train(path_data=DIR_DATA, batch=16, epochs=1)

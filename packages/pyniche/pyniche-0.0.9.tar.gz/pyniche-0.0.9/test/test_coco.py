import sys
import os
import json
import random
from PIL import Image

# torch imports
import torchvision

os.chdir("..")
sys.path.append(".")

ROOT = os.getcwd()


class CocoDetectionDataset(torchvision.datasets.CocoDetection):
    def __init__(self, root, file_json, processor):
        """
        prerequisite: json file must be placed in root/labels/
        args:
            root: root directory of the dataset
            file_json: json file name, e.g. _coco_train.json
            processor: pre-trained transformation pipeline (can it be other than DETR?)
        """
        self.root = root
        self.processor = processor
        path_json = os.path.join(root, "labels", file_json)
        super().__init__(root, path_json)

    def _load_image(self, id: int) -> Image.Image:
        # optional
        image_name = self.coco.loadImgs(id)[0]["file_name"]
        image_path = os.path.join(self.root, "images", image_name)
        image = Image.open(image_path).convert("RGB")
        return image

    def __getitem__(self, idx):
        # read in PIL image and target in COCO format
        # feel free to add data augmentation here before passing them to the next step
        img, target = super().__getitem__(idx)

        return img, target
        # # preprocess image and target (converting target to DETR format, resizing + normalization of both image and target)
        # image_id = self.ids[idx]
        # target = {"image_id": image_id, "annotations": target}
        # encoding = self.processor(images=img, annotations=target, return_tensors="pt")
        # pixel_values = encoding["pixel_values"].squeeze()  # remove batch dimension
        # target = encoding["labels"][0]  # remove batch dimension

        # return pixel_values, target


from transformers import DetrForObjectDetection, DetrImageProcessor

root_data = os.path.join(
    ROOT,
    "pyniche",
    "data",
    "examples",
    "balloon",
)
path_model = "facebook/detr-resnet-50"
processor = DetrImageProcessor.from_pretrained(path_model)
dataset = CocoDetectionDataset(root_data, "_coco_test.json", processor=processor)
idx = 1
img, target = dataset[1]
coco = dataset.coco



# get filename
ids = coco.getImgIds()
meta_img = coco.loadImgs(ids)

meta = meta_img[0]
filename = meta["file_name"]
img_id = meta["id"]
ann_ids = coco.getAnnIds(img_id)
annotations = coco.loadAnns(ann_ids)

annotation = annotations[0]
annotation["id"]
annotation["category_id"]
coco.cats[annotation["category_id"]]["supercategory"]
annotation["bbox"]
annotation["area"]


len(annotations)
meta
coco.getImgIds()


coco.imgs.keys()

# len
coco.loadImgs(1)
coco.showAnns(coco.loadAnns(1))
coco.loadAnns(1)


image_id = dataset.ids[idx]

target = {"image_id": image_id, "annotations": target}
encoding = processor(images=img, annotations=target, return_tensors="pt")
target

encoding.keys()
len(encoding["labels"])
pixel_values.size()
encoding["pixel_values"].size()
pixel_values = encoding["pixel_values"].squeeze()  # remove batch dimension
target = encoding["labels"][0]  # remove batch dimension
target

features=datasets.Features(
    {
        "image": datasets.Image(),
        "annotations": datasets.Sequence(
            {
                "id": datasets.Value("int64"),
                "supercategory": datasets.ClassLabel(names=COCO_SUPCLASSES),
                "category": datasets.ClassLabel(names=COCO_CLASSES),
                "bbox": datasets.Sequence(datasets.Value("float64"), length=4),
                "area": datasets.Value("float64"),
            }),
        "image_id": datasets.Value("int64"),
        "filename": datasets.Value("string"),
    }
),
homepage="githu
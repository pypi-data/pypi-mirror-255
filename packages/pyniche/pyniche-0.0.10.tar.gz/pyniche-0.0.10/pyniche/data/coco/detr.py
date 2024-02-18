"""
This module is used to process HuggingFace's DETR COCO dataset to be used with LightningDataModule.

"""

# native
import numpy as np

# local imports
from pyniche.data.base import BaseDataModule
from pyniche.data.bbox import resize_bbox, xywh2xyxy

# deep learning
import torch
from transformers import DetrImageProcessor
import albumentations as A
import torchvision.transforms as T

import supervision as sv

# CONSTANTS
PROCESSOR = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")


class DetectDataModule(BaseDataModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_labels(self, split):
        """
        extract labels from dataloader and flatten them to (N, )
        """
        dataloader = self.get_dataloader(split)
        labels = []
        for batch in iter(dataloader):
            labels += [{k: v for k, v in t.items()} for t in batch["labels"]]
        return labels

    def get_pixels(self, split):
        """
        extract padded pixels from dataloader and flatten them to (N, )
        """
        dataloader = self.get_dataloader(split)
        pixels = []
        for batch in iter(dataloader):
            pixels += batch["pixel_values"]
        return pixels

    def get_images(self, split):
        """
        extract images from dataloader and flatten them to (N, )
        """
        dataset = self.get_dataset(split)
        return dataset["image"]

    def get_detections(self, split):
        """
        transform the labels to sv.Detections
        """
        labels = self.get_labels(split)
        return [label2detect(l) for l in labels]

    def _collate_fn(self, batch):
        """
        Turn a list of structs into a struct of arrays.

        param
        ---
        batch
            - sample 1
                - pixel_values
                - pixel_mask
                - labels
                    - image_id
                    - annotations
                        - id
                        - image_id
                        - category_id
                        - bbox
                        - iscrowd
                        - area
                        - segmentation
            - sample 2
                - pixel_values
                - pixel_mask
                - labels

        return
        ---
        a dict
            - pixel_values
                - sample 1
                - sample 2
                ...
            - pixel_mask
                - sample 1
                - sample 2
                ...
            - labels
                - sample 1
                - sample 2
                ...
        """
        new_batch = {}
        new_batch["pixel_values"] = torch.stack(
            [item["pixel_values"] for item in batch]
        )
        new_batch["pixel_mask"] = torch.stack([item["pixel_mask"] for item in batch])
        new_batch["labels"] = [item["labels"] for item in batch]
        return new_batch

    def _collate_fn_train(self, batch):
        return self._collate_fn(batch)

    def _collate_fn_val(self, batch):
        return self._collate_fn(batch)

    def _collate_fn_test(self, batch):
        return self._collate_fn(batch)

    def _transform_train(self, examples):
        """
        input
        ---
        examples (a struct of arrays, SOA)
            image
                image 1
                image 2
                ...
            image_id
                image_id 1
                image_id 2
                ...
            ...
            annotations
                annotation 1
                    id
                        id 1
                        id 2
                        ...
                    image_id
                        image_id 1
                        image_id 1
                        ...
                    ...
                annotation 2
                    ...
                ...

        output
        ---
        batch (an array of structs, AOS)
            example 1
                pixel_values
                pixel_mask
                labels
                    size
                    image_id
                    class_labels
                        label 1
                        label 2
                        ...
                    boxes
                        box 1
                        box 2
                        ...
                    area
                        area 1
                        area 2
                        ...
                    iscrowd
                        iscrowd 1
                        iscrowd 2
                        ...
                    orig_size
            example 2
            ...

        # REFERENCE
        https://albumentations.ai/docs/getting_started/bounding_boxes_augmentation/
        """

        transform = A.Compose(
            [
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.5),
                A.RandomBrightnessContrast(p=1),
            ],
            bbox_params=A.BboxParams(
                format="coco",
                label_fields=["category"],
            ),
        )
        batch = process(examples, transform)
        return batch

    def _transform_val(self, examples):
        transform = A.Compose(
            [],
            bbox_params=A.BboxParams(
                format="coco",
                label_fields=["category"],
            ),
        )
        batch = process(examples, transform)
        return batch

    def _transform_test(self, examples):
        transform = A.Compose(
            [],
            bbox_params=A.BboxParams(
                format="coco",
                label_fields=["category"],
            ),
        )
        batch = process(examples, transform)
        return batch


# FIXME: add the block to the albumenation library
"""
In albumentations/core/bbox_utils.py

def check_bbox(bbox: BoxType) -> None:
    # check bbox range
    bbox=list(bbox)
    for i in range(4):
      if (bbox[i]<0) :
        bbox[i]=0
      elif (bbox[i]>1) :
        bbox[i]=1
    bbox=tuple(bbox)
    # rest of the code
"""


def process(examples, transform):
    transformed_images = []
    transformed_anns = []
    for image, image_id, annotations in zip(
        examples["image"], examples["image_id"], examples["annotations"]
    ):
        # image
        image = np.array(image.convert("RGB"))[:, :, ::-1]

        out = transform(
            image=image,
            bboxes=annotations["bbox"],
            category=annotations["category_id"],
        )
        ann = {
            "image_id": image_id,
            "annotations": [
                {
                    "id": annotations["id"][i],
                    "image_id": annotations["image_id"][i],
                    "category_id": out["category"][i],
                    "bbox": out["bboxes"][i],
                    "iscrowd": annotations["iscrowd"][i],
                    "area": annotations["area"][i],
                    "segmentation": annotations["segmentation"][i],
                }
                for i in range(len(annotations["id"]))
            ],
        }
        # append
        transformed_images.append(out["image"])
        transformed_anns.append(ann)
    # process the transformed data
    batch = PROCESSOR(
        images=transformed_images,
        annotations=transformed_anns,
        return_tensors="pt",
    )
    return batch


def label2detect(label):
    size = label["size"]
    class_id = label["class_labels"].numpy()
    bbox = [resize_bbox(b, size) for b in label["boxes"]]
    bbox = np.array([xywh2xyxy(b) for b in bbox])
    return sv.Detections(xyxy=bbox, class_id=class_id)

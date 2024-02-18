"""
A class to modify COCO json files.

methods
---
- i/o
    - load
    - save

- subsetting
    - subset_by_dir
    - subset_by_image_ids

- getters
    - get_filenames_from_dir
    - get_ids_from_imgs
    - get_img_by_filename
    - get_img_by_image_id
    - get_ann_by_image_id

- concatenate
"""

# native imports
import json
import os
import numpy as np
import PIL

# local imports
from pyniche.data.bbox import xywh2xyxy

# deep learning
import supervision as sv


class COCO_API:

    def __init__(
        self,
        path_json=None,
        data=None,
    ):
        # members
        self.data = data  # user-provided dict of COCO keys
        self.path_json = path_json
        # init
        if not data:
            # 2. user provided path to json
            self.load()

        # load filepaths
        self.filepaths = self.get_filepaths_from_imgs(self.images())
        self.image_ids = self.get_ids_from_imgs(self.images())

    def load(self):
        with open(self.path_json, "r") as f:
            self.data = json.load(f)

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f)

    def new_instance(self, imgs_coco, ann_coco):
        # re-index images and annotations
        # imgs_coco, ann_coco = reindex_coco(imgs_coco, ann_coco)

        # new instance
        new_json = dict(
            {
                "info": self.info(),
                "licenses": self.licenses(),
                "categories": self.categories(),
                "images": imgs_coco,
                "annotations": ann_coco,
            }
        )
        return COCO_API(data=new_json)

    # subsetting
    def subset_by_dir(self, dir_img):
        # get images from dir
        filenames = self.get_filenames_from_dir(dir_img)
        imgs_coco = self.get_img_by_filename(filenames)

        # get ann by ids of images
        ids = self.get_ids_from_imgs(imgs_coco)
        ann_coco = self.get_ann_by_image_id(ids)

        # return
        return self.new_instance(imgs_coco, ann_coco)

    def subset_by_image_ids(self, ids):
        if isinstance(ids, int):
            # if int, it's a single id
            ids = [ids]
        elif isinstance(ids, list):
            # if list, it's a list of ids
            ids = ids
        elif isinstance(ids, tuple):
            # if tuple, it's a range
            ids = list(np.arange(ids[0], ids[1] + 1))

        # filter images
        imgs_coco = self.get_img_by_image_id(ids)
        ann_coco = self.get_ann_by_image_id(ids)

        # return
        return self.new_instance(imgs_coco, ann_coco)

    # getters
    def get_detections(self):
        """
        get sv.Detections from COCO annotations

        return
        ------
        a list of sv.Detections
        """
        detections = []
        img_ids = self.get_ids_from_imgs(self.images())
        for id in img_ids:
            anns = self.get_ann_by_image_id([id])
            ls_xyxy = []
            ls_cls = []
            for ann in anns:
                xywh = ann["bbox"]
                cls = ann["category_id"]
                xyxy = xywh2xyxy(xywh, in_xy="top-left")
                ls_xyxy.append(xyxy)
                ls_cls.append(cls)
            ls_xyxy = np.array(ls_xyxy)
            ls_cls = np.array(ls_cls)
            detections.append(sv.Detections(ls_xyxy, class_id=ls_cls))
        return detections

    def get_PIL(self, idx):
        filepath = self.filepaths[idx]
        img = PIL.Image.open(filepath)
        return img

    def get_filepaths_from_imgs(self, imgs_coco):
        path_dir = os.path.dirname(self.path_json)
        filepaths = [os.path.join(path_dir, i["file_name"]) for i in imgs_coco]
        return filepaths

    def get_filenames_from_dir(self, dir_img):
        filenames = [f for f in os.listdir(dir_img) if ".jpg" in f or ".png" in f]
        return sorted(filenames)

    def get_ids_from_imgs(self, imgs_coco):
        ids = [i["id"] for i in imgs_coco]
        return ids

    def get_img_by_filename(self, filenames):
        imgs_coco = [i for i in self.images() if i["file_name"] in filenames]
        return imgs_coco

    def get_img_by_image_id(self, ids):
        imgs_coco = [i for i in self.images() if i["id"] in ids]
        return imgs_coco

    def get_ann_by_image_id(self, ids):
        ann_coco = [a for a in self.annotations() if a["image_id"] in ids]
        return ann_coco

    # concat
    def concatenate(self, coco):
        """
        both self and coco are COCO_API instances
        """
        # check the self data and max id
        imgs_self = self.images()
        ann_self = self.annotations()

        # check the coco data and reinex
        imgs_coco = coco.images()
        ann_coco = coco.annotations()
        # add 10000 to the coco id
        for i, img in enumerate(imgs_coco):
            imgs_coco[i]["id"] += 10000
        for i, ann in enumerate(ann_coco):
            ann_coco[i]["id"] += 10000
            ann_coco[i]["image_id"] += 10000
        # concatenate
        imgs_new = imgs_self + imgs_coco
        ann_new = ann_self + ann_coco
        return self.new_instance(imgs_new, ann_new)

    # COCO keys
    def info(self):
        return self.data["info"]

    def licenses(self):
        return self.data["licenses"]

    def categories(self):
        return self.data["categories"]

    def images(self):
        return self.data["images"]

    def annotations(self):
        return self.data["annotations"]

import os
import json
from PIL import Image
import datasets


def hf_to_yolo(
    datadict,
    dir_dest,
    classes=["category 1"],
    size_new=None,
):
    """
    iteratively extract Dataset from DatasetDict and save to YOLO format

    param
    ----
    datadict: DatasetDict
    dir_dest: str
        destination folder
    size_new: tuple
        (width, height)
    classes: list
        list of class names

    output
    ---
    dir_dest/
        data.yaml
        <split_1>.txt
        <split_2>.txt
        <split_1>/
            images/
                image_1.jpg
                image_2.jpg
                ...
            labels/
                image_1.txt
                image_2.txt
                ...
        <split_2>/
            ...
    """
    splits = []
    for split in datadict:
        print(f"Processing split: {split}")
        splits.append(split)
        split_dir = os.path.join(dir_dest, split)
        split_file = os.path.join(dir_dest, f"{split}.txt")
        filenames = _hf_to_yolo(datadict[split], split_dir, size_new)
        with open(split_file, "a") as f:
            for filename in filenames:
                f.write(os.path.join(split_dir, "images", filename) + "\n")

    # Create data.yaml file
    yaml_path = os.path.join(dir_dest, "data.yaml")
    with open(yaml_path, "w") as yaml_file:
        yaml_file.write("path: %s\n" % dir_dest)
        yaml_file.write("nc: %d\n" % len(classes))
        # splits
        for split in splits:
            yaml_file.write(f"{split}: {split}.txt\n")
        # classes
        yaml_file.write("names:\n")
        for i, class_name in enumerate(classes):
            yaml_file.write(f"  {i}: {class_name}\n")


def _hf_to_yolo(
    dataset,
    dir_dest,
    size_new=None,
):
    """
    turn one dataset instance to YOLO format and save to dir_dest

    param
    ----
    dataset: Dataset instance
    dir_dest: str
        destination folder
    size_new: tuple
        (width, height)

    output
    ---
    dir_dest/
        images/
            image_1.jpg
            image_2.jpg
            ...
        labels/
            image_1.txt
            image_2.txt
    """
    # Create directories
    os.makedirs(os.path.join(dir_dest, "images"), exist_ok=True)
    os.makedirs(os.path.join(dir_dest, "labels"), exist_ok=True)

    # extract dataset
    ls_annotations = dataset["annotations"]
    ls_filename = dataset["filename"]
    ls_image = dataset["image"]

    # Process each image and annotation
    for i in range(len(dataset)):
        # log
        filename = ls_filename[i]
        print("(%d/%d) %s\r" % (i + 1, len(dataset), filename))

        # image
        image_path = os.path.join(dir_dest, "images", filename)
        image = ls_image[i]
        size_ori = image.size
        if size_new:
            image = image.resize(size_new, Image.Resampling.LANCZOS)
        else:
            size_new = size_ori
        image.save(image_path)

        # label
        label_path = os.path.join(dir_dest, "labels", filename.replace(".jpg", ".txt"))
        with open(label_path, "w") as label_file:
            for annotation, bbox in zip(
                ls_annotations[i]["category_id"],
                ls_annotations[i]["bbox"],
            ):
                # Scale bbox coordinates
                scale_x = size_new[0] / size_ori[0]
                scale_y = size_new[1] / size_ori[1]
                scaled_bbox = [
                    bbox[0] * scale_x,
                    bbox[1] * scale_y,
                    bbox[2] * scale_x,
                    bbox[3] * scale_y,
                ]

                # Convert scaled bbox to YOLO format
                x_center = (scaled_bbox[0] + scaled_bbox[2] / 2) / size_new[0]
                y_center = (scaled_bbox[1] + scaled_bbox[3] / 2) / size_new[1]
                width = scaled_bbox[2] / size_new[0]
                height = scaled_bbox[3] / size_new[1]

                # Write to label file
                # minus 1 because YOLO uses 0-based class index
                label_file.write(
                    f"{annotation - 1} {x_center} {y_center} {width} {height}\n"
                )
    # return filenames
    return ls_filename


def hf_to_coco(
    datadict,
    dir_dest,
    classes=["category 1"],
    size_new=None,
):
    """
    param
    ---
    datadict: DatasetDict
    dir_dest: str
        destination folder
    size_new: tuple
        (width, height)
    classes: list
        list of class names

    output
    ---
    dir_dest/
        <split_1>/
            data.json
            image_1.jpg
            image_2.jpg
            ...
        <split_2>/
            ...
        ...
    """
    splits = []
    for split in datadict:
        print(f"Processing split: {split}")
        splits.append(split)
        split_dir = os.path.join(dir_dest, split)
        os.makedirs(split_dir, exist_ok=True)
        _hf_to_coco(datadict[split], split_dir, classes, size_new)


def _hf_to_coco(
    dataset,
    dir_dest,
    classes=["category 1"],
    size_new=None,
):
    """
    param
    ---
    dataset: Dataset instance
    dir_dest: str
        destination folder
    size_new: tuple
        (width, height)
    classes: list
        list of class names

    output
    ---
    dir_dest/
        data.json
        image_1.jpg
        image_2.jpg
        ...
    """
    coco_format = {
        "info": {},
        "licenses": [],
        "categories": [],
        "images": [],
        "annotations": [],
    }
    # extract dataset
    ls_annotations = dataset["annotations"]
    ls_imgage_id = dataset["image_id"]
    ls_filename = dataset["filename"]
    ls_image = dataset["image"]

    category_set = set()
    for i in range(len(dataset)):
        # Process categories
        for category_id in ls_annotations[i]["category_id"]:
            category_set.add(category_id)

    # Add categories
    for i, category_id in enumerate(category_set):
        try:
            coco_format["categories"].append(
                {
                    "id": category_id,
                    "name": classes[i],
                    "supercategory": classes[i],
                }
            )
        except:
            raise ValueError(
                f"Number of classes ({len(classes)}) should match the number of unique categories ({len(category_set)})"
            )

    annotation_id = 1  # Initialize annotation ID
    for i in range(len(dataset)):
        image_id = ls_imgage_id[i]
        filename = ls_filename[i]
        image = ls_image[i]
        img_w, img_h = image.size

        print("(%d/%d) %s\r" % (i + 1, len(dataset), filename))

        # Resize image if size_new is provided
        if size_new:
            image = image.resize(size_new, Image.Resampling.LANCZOS)
        image.save(os.path.join(dir_dest, filename))

        # Add image information
        coco_format["images"].append(
            {
                "id": image_id,
                "width": image.width,
                "height": image.height,
                "file_name": filename,
            }
        )

        # Add annotations
        for category_id, bbox in zip(
            ls_annotations[i]["category_id"], ls_annotations[i]["bbox"]
        ):
            # Scale bbox if image is resized
            if size_new:
                scale_x = size_new[0] / img_w
                scale_y = size_new[1] / img_h
                scaled_bbox = [
                    bbox[0] * scale_x,  # x
                    bbox[1] * scale_y,  # y
                    bbox[2] * scale_x,  # w
                    bbox[3] * scale_y,  # h
                ]
            else:
                scaled_bbox = bbox

            coco_format["annotations"].append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": scaled_bbox,
                    "area": scaled_bbox[2] * scaled_bbox[3],  # width * height
                    "iscrowd": 0,  # Assuming individual objects
                }
            )
            annotation_id += 1
    # Write to JSON file
    with open(os.path.join(dir_dest, "data.json"), "w") as f:
        json.dump(coco_format, f, indent=4)

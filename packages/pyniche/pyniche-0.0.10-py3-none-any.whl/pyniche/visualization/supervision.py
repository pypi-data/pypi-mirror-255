import numpy as np
import supervision as sv
import matplotlib.pyplot as plt


def vis_detections(
    image,
    detections,
    text="object",
    thickness=2,
    figsize=(20, 10),
):
    """
    img: PIL.Image for the annotation to be drawn on
    detections: sv.Detection
    text: text annotations, e.g., "balloon". If None, no text is drawn
    """

    ann_bbox = sv.BoundingBoxAnnotator(thickness=thickness)
    ann_text = sv.LabelAnnotator(text_position=sv.Position.BOTTOM_LEFT)

    # draw predictions
    att_frame_pred = ann_bbox.annotate(np.array(image), detections)
    if text:
        text_ann = [f"{text}" for _ in range(len(detections))]
        att_frame_pred = ann_text.annotate(
            att_frame_pred,
            detections,
            labels=text_ann,
        )
    plt.figure(figsize=figsize)
    plt.imshow(att_frame_pred)

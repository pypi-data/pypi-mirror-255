import os
import json
import time
from ultralytics import YOLO


class NicheYOLO:
    def __init__(self, path_model):
        """
        path_model: str
            path to model.pt
            yolov8n.pt
            yolov8s.pt
            yolov8m.pt
            yolov8l.pt
            yolov8x.pt

        Folder structure
        models/
            <path_model>.pt (options: yolov8n.pt yolov8s.pt yolov8m.pt yolov8l.pt yolov8x.pt)
        out/
            train/
                <name_task>/
                    weights/
                        best.pt
                    ...
            val/
                <name_task>/
                    results.json
                    ...

        """
        # attributes
        self.model = YOLO(path_model)
        print("model %s loaded" % path_model)

    def train(
        self,
        path_yaml,  # path to data.yaml
        name_task,
        batch=16,
        epochs=100,
        device="cuda",  # "mps", or cpu
    ):
        """
        <project>/
            <name_task>/
                weights/
                    best.pt
                ...
        """
        start = time.time()
        self.model.train(
            data=path_yaml,
            batch=batch,
            epochs=epochs,
            device=device,
            project=".",
            name=name_task,
            exist_ok=True,
        )
        time_elapsed = time.time() - start
        best_model = os.path.join(name_task, "weights", "best.pt")
        self.model = YOLO(best_model)
        return time_elapsed

    def evaluate(
        self,
        name_task,
        split="test",
        device="cuda",
    ):
        metrics = self.model.val(
            split=split,
            device=device,
            project=".",
            name=name_task,
            exist_ok=True,
        )
        return ext_metrics(metrics)


def ext_metrics(metrics):
    # source
    # ultralytics.utils.metrics.DetMetrics
    """
    args
    ----
        metrics: dict
            metrics from model.val()

    return
    ------
        json: dict
    """
    # metrics
    map5095 = metrics.box.map.round(4)
    map50 = metrics.box.map50.round(4)
    precision = metrics.box.p[0].round(4)
    recall = metrics.box.r[0].round(4)
    f1 = metrics.box.f1[0].round(4)
    # confusion matrix
    conf_mat = metrics.confusion_matrix.matrix  # conf=0.25, iou_thres=0.45
    n_all = conf_mat[:, 0].sum()
    n_fn = conf_mat[1, 0].sum()
    n_fp = conf_mat[0, 1].sum()
    # write json
    json_out = dict(
        map5095=map5095,
        map50=map50,
        precision=precision,
        recall=recall,
        f1=f1,
        n_all=int(n_all),
        n_fn=int(n_fn),  # false negative
        n_fp=int(n_fp),
    )
    return json_out

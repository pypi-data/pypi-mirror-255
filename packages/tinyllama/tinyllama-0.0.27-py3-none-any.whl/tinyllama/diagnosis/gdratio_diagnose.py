from collections import defaultdict
from tqdm import tqdm
from copy import deepcopy

import torch
import matplotlib.pyplot as plt

from ..models import Llama
from ..training import Trainer, TrainConfig
from ..diagnosis import Diagnose


class GdrDiagnose(Diagnose):
    def __init__(self, *, num_iters: int, num_params_to_track: int, hide_legend: bool = True):
        self.num_iters = num_iters
        self.num_params_to_track = num_params_to_track
        self.hide_legend = hide_legend

    def run(self, model: Llama, tokens: torch.Tensor, TRAIN_CONFIG: TrainConfig):
        model_clone = deepcopy(model)

        TRAIN_CONFIG["epochs"] = 1
        Trainer_ = Trainer(TRAIN_CONFIG)

        # necessary initial training job, data can't be found from deepcopy otherwise.
        Trainer_.run(model_clone, tokens, hide_progress=True)

        gd_records = defaultdict(list)
        for _ in tqdm(range(self.num_iters), colour="green"):

            # retrieve data for each param before training
            for count, elem in enumerate(model_clone.named_parameters()):
                if elem[1].grad is not None:
                    gd_records[elem[0]].append(
                         1 / elem[1].detach().cpu().std()
                    )
                if count > self.num_params_to_track:
                    break

            Trainer_.run(model_clone, tokens, hide_progress=True)

            # compute gdratio (lr*grad)/data for each param after training
            for count, elem in enumerate(model_clone.named_parameters()):
                if elem[1].grad is not None:
                    gd_records[elem[0]][-1] = gd_records[elem[0]][-1]*elem[1].grad.detach().cpu().std()*TRAIN_CONFIG["lr"] 
                if count > self.num_params_to_track:
                    break

        for name, gdr_list in gd_records.items():
            name = ".".join(name.split(".")[-2:])
            # legends.append(f"Param name: {name}")
            plt.plot(gdr_list)

        # recommended threshold
        plt.axhline(y=1e-3, color='r', linestyle='--')

        plt.title("Gradient/Data ratio across multiple runs")
        plt.show()

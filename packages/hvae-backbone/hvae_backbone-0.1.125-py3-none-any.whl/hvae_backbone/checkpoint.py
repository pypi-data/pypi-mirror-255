import torch
import os
from .utils import wandb_log_checkpoint


class Checkpoint:
    """
    Checkpoint class for saving and loading experiments
    """
    def __init__(self, global_step=-1, model=None, optimizer=None, scheduler=None, params=None):
        try:
            self.global_step: int = global_step
            self.model = model
            self.params = params

            self.scheduler_state_dict = scheduler.state_dict() if scheduler is not None else None
            self.optimizer_state_dict = optimizer.state_dict() if optimizer is not None else None
        except TypeError:
            print("Error loading experiment")

    def save(self, path, run=None):
        checkpoint_dir = os.path.join(path, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, "model.pth")
        torch.save(self, checkpoint_path)

        if run is not None:
            wandb_log_checkpoint(run, checkpoint_path, self.params.log_params.name)
        return checkpoint_path

    def save_migration(self, path):
        os.makedirs(path, exist_ok=True)
        checkpoint_path = os.path.join(path, f"migrated_checkpoint.pth")
        torch.save(self, checkpoint_path)
        return checkpoint_path

    @staticmethod
    def load(path):
        experiment: Checkpoint = torch.load(path, map_location='cpu')
        return experiment

    def get_model(self):
        return self.model

    def __getstate__(self):
        from .sequence import hSequenceVAE
        return {
                "global_step": self.global_step,
                "model":       self.model.serialize(),
                "scheduler_state_dict": self.scheduler_state_dict,
                "optimizer_state_dict": self.optimizer_state_dict,
                "sequential": isinstance(self.model, hSequenceVAE)
                }

    def __setstate__(self, state):
        from .hvae import hVAE
        from .sequence import hSequenceVAE

        self.global_step = state["global_step"]
        self.model = hVAE.deserialize(state["model"]) if not state["sequential"] \
            else hSequenceVAE.deserialize(state["model"])
        self.scheduler_state_dict = state["scheduler_state_dict"]
        self.optimizer_state_dict = state["optimizer_state_dict"]



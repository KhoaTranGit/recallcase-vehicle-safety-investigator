"""Reproducibility helpers for RecallCase experiments.

Call seed_all() near the start of each experiment, before creating models,
sampling data, or initializing CUDA. This cannot guarantee deterministic
results from external LLM APIs or across different hardware/library versions.
"""

import os
import random


def seed_all(seed: int = 42, deterministic: bool = True) -> None:
    """Seed Python, NumPy, PyTorch (CPU/CUDA), and TensorFlow if installed.

    Args:
        seed: Nonnegative integer random seed.
        deterministic: Request deterministic PyTorch algorithms when available.
            Some operations may raise if no deterministic implementation exists.
    """
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")

    # Set before starting Python to affect hash randomization for this process;
    # setting it here primarily propagates it to child processes.
    os.environ["PYTHONHASHSEED"] = str(seed)
    # For CUDA deterministic operations, set before CUDA is initialized.
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

    random.seed(seed)

    try:
        import numpy as np
    except ImportError:
        pass
    else:
        np.random.seed(seed)  # np.random.default_rng() needs its own explicit seed.

    try:
        import torch
    except ImportError:
        pass
    else:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            torch.use_deterministic_algorithms(True)

    try:
        import tensorflow as tf
    except ImportError:
        pass
    else:
        tf.keras.utils.set_random_seed(seed)
        if deterministic:
            tf.config.experimental.enable_op_determinism()


if __name__ == "__main__":
    seed_all()
    print("Random seeds initialized (seed=42).")

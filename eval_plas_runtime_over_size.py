import torch
import numpy as np
import random
import pandas as pd
import time
from datetime import datetime

from vad import compute_vad
from random_grid import generate_random_colors
from plas import sort_with_plas


def runtime_over_size(device):

    print(f"Running benchmark on {device}...")

    benchmark_start_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    df = pd.DataFrame(columns=["i", "size", "duration", "vad"])

    for i in range(4, 7):

        size = 2**i

        params_np = generate_random_colors(size, size)

        # (channels, height, width)
        params = torch.from_numpy(params_np).permute(2, 0, 1).float().to(device)
        assert params.shape[1] == params.shape[2]

        start = time.time()

        sorted_params, sorted_indices = sort_with_plas(
            params.clone(), improvement_break=1e-4, verbose=False
        )

        duration = time.time() - start

        assert (
            params.to(torch.int64).sum().item()
            == sorted_params.to(torch.int64).sum().item()
        )

        vad = compute_vad(sorted_params.permute(1, 2, 0).cpu().numpy())

        print(f"{i=} {size=} {duration=:.2f} {vad=:.4f}")

        df.loc[df.shape[0]] = [i, size, duration, vad]

    print(df)
    df.to_csv(f"{benchmark_start_time}_runtime_over_size_{device}.csv", index=False)


if __name__ == "__main__":
    if torch.backends.mps.is_available():
        runtime_over_size(torch.device("mps"))

    if torch.cuda.is_available():
        runtime_over_size(torch.device("cuda"))

    runtime_over_size(torch.device("cpu"))
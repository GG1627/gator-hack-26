"""Baseline schedules depend only on public metadata and seed."""
import numpy as np


class ScheduledPolicy:
    def __init__(self, name):
        if name not in ("fixed_interval", "seeded_random"):
            raise ValueError(f"Unknown policy: {name}")
        self.name = name

    def reset(self, metadata, budget, seed):
        total = metadata.frame_count
        if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= total:
            raise ValueError(f"budget must be an integer in [1, {total}]")
        if self.name == "fixed_interval":
            # Integer floor of endpoint-inclusive linspace. B=1 captures only 0.
            indices = [0] if budget == 1 else [k * (total - 1) // (budget - 1) for k in range(budget)]
        else:
            indices = [0, *np.random.default_rng(seed).choice(np.arange(1, total), size=budget-1, replace=False).tolist()]
        self.indices = frozenset(indices)

    def decide(self, t, past_observations):
        return t in self.indices

    def observe(self, frame):
        pass

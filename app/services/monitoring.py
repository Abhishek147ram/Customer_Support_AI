from collections import Counter, defaultdict
from typing import Dict, List

from app.config.logger import logger


class MetricsCollector:
    def __init__(self) -> None:
        self.counters = Counter()
        self.histograms: Dict[str, List[float]] = defaultdict(list)

    def increment(self, metric_name: str, amount: int = 1) -> None:
        self.counters[metric_name] += amount
        logger.debug(f"Metric incremented {metric_name} by {amount}")

    def record_latency(self, metric_name: str, duration: float) -> None:
        self.histograms[metric_name].append(duration)
        logger.debug(f"Metric latency recorded {metric_name} duration={duration:.4f}")

    def get_metrics(self) -> Dict[str, float]:
        metrics = {name: value for name, value in self.counters.items()}
        for name, values in self.histograms.items():
            if values:
                metrics[f"{name}_count"] = len(values)
                metrics[f"{name}_sum"] = sum(values)
                metrics[f"{name}_avg"] = sum(values) / len(values)
        return metrics

    def exposition_text(self) -> str:
        lines = []
        for metric, value in sorted(self.get_metrics().items()):
            lines.append(f"{metric} {value}")
        return "\n".join(lines)

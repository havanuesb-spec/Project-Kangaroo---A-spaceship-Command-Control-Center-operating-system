from dataclasses import dataclass, asdict
from copy import deepcopy

@dataclass
class HealthMetrics:
    weight_kg: float
    resting_hr: int
    systolic_bp: int
    diastolic_bp: int
    sleep_hours: float
    steps_per_day: int

class HealthRecord:
    def __init__(self, patient_name: str, baseline: HealthMetrics):
        self.patient_name = patient_name
        self.baseline = deepcopy(baseline)
        self.current = deepcopy(baseline)
        self.history = [("baseline_loaded", asdict(self.current))]

    def update_current(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self.current, k):
                setattr(self.current, k, v)
            else:
                raise ValueError(f"Unknown metric: {k}")
        self.history.append(("updated", asdict(self.current)))

    def restore_to_baseline(self):
        self.current = deepcopy(self.baseline)
        self.history.append(("restored_to_baseline", asdict(self.current)))

    def snapshot(self):
        return {
            "patient_name": self.patient_name,
            "current": asdict(self.current),
            "baseline": asdict(self.baseline),
            "history_events": len(self.history),
        }

if __name__ == "__main__":
    may_2019_baseline = HealthMetrics(
        weight_kg=78.4,
        resting_hr=62,
        systolic_bp=120,
        diastolic_bp=78,
        sleep_hours=7.4,
        steps_per_day=8500
    )

    record = HealthRecord("Joe", may_2019_baseline)
    record.update_current(weight_kg=83.1, resting_hr=71, sleep_hours=6.1)
    print("Before restore:", record.snapshot()["current"])

    record.restore_to_baseline()
    print("After restore:", record.snapshot()["current"])

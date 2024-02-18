from dataclasses import dataclass

import pandas as pd


@dataclass
class TimeInterval:
    left: pd.Timestamp
    right: pd.Timestamp

    def __post_init__(self):
        self.left = pd.Timestamp(self.left)
        self.right = pd.Timestamp(self.right)

    def shift(self, period: pd.Timedelta) -> "TimeInterval":
        return TimeInterval(
            left=self.left + period,
            right=self.right + period,
        )

    def to_range(self, freq: pd.Timedelta, name: str = "time_utc") -> pd.DatetimeIndex:
        return pd.date_range(self.left, self.right, freq=freq, name=name)

    def isoformat(self) -> str:
        return f"{self.left.isoformat()}/{self.right.isoformat()}"

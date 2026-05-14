from abc import ABC, abstractmethod
from typing import Any, Hashable

import pandas as pd
from pandas import DataFrame


class CalculationStrategy(ABC):
    """计算的抽象基类"""

    @abstractmethod
    def execute(self, df: DataFrame, **kwargs) -> Any:
        pass


class TotalRowStrategy(CalculationStrategy):
    def execute(self, df: DataFrame, **kwargs) -> int:
        return len(df)


class DateRangeStrategy(CalculationStrategy):
    def execute(
        self, df: DataFrame, column: str | None, **kwargs
    ) -> dict[str, Any] | None:

        if df.empty or not column or column not in df.columns:
            return None

        dates = pd.to_datetime(df[column], errors="coerce").dropna()

        if dates.empty:
            return None

        return {"start": dates.min(), "end": dates.max()}


class ConditionalCountStrategy(CalculationStrategy):
    def execute(
        self, df: DataFrame, column: str | None = None, value: Any = None, **kwargs
    ) -> int:
        if df.empty or not column or column not in df.columns or value is None:
            return 0
        return int((df[column] == value).sum())


class ValueCountStrategy(CalculationStrategy):
    def execute(
        self, df: DataFrame, column: str | None = None, **kwargs
    ) -> dict[Hashable, Any]:

        if df.empty or not column or column not in df.columns:
            return {}
        return df[column].value_counts().to_dict()


calculation_registry: dict[str, CalculationStrategy] = {
    "total_rows": TotalRowStrategy(),
    "date_range": DateRangeStrategy(),
    "conditional_count": ConditionalCountStrategy(),
    "value_counts": ValueCountStrategy(),
}

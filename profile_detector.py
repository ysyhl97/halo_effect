from typing import Any

from pandas import DataFrame


def detect_profile(df: DataFrame, profiles: dict[str, Any]) -> dict[str, Any] | None:
    """
    判断哪个profile，更符合当前表格。没有符合的，就返回None
    """

    best_match_profile = None
    max_match_count = 0

    for profile_key, profile_data in profiles.items():
        if profile_key == "default":
            continue

        mapping = profile_data.get("column_mapping", {})
        if not mapping:
            continue

        match_count = sum(1 for col_name in mapping.values() if col_name in df.columns)

        if match_count > 0 and match_count > max_match_count:
            max_match_count = match_count
            best_match_profile = profile_data

    if max_match_count == 0:
        return None

    return best_match_profile

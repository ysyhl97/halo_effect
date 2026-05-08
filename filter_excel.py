import functools
import json
import logging
import operator
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from pandas import DataFrame

logger = logging.getLogger(__name__)


def load_folder(folder: str = r"./source") -> list:
    """加载目录"""

    file_folder = Path(folder)

    if not file_folder.exists():
        logger.error(f"路径不存在,请进行检查：{file_folder}")
        return None
    logger.info(f"正在加载路径目录：{folder}")
    exist_suffix = [".xlsx", ".xls"]

    excel_files_path = [
        file for file in file_folder.rglob("*") if file.suffix in exist_suffix
    ]
    if not excel_files_path:
        logger.warning(f"{file_folder}中没有找到excel文件")
        return

    logger.info(f"共找到{len(excel_files_path)}个excel文件,准备处理....")

    return excel_files_path


def load_all_sheet(file_path: str) -> DataFrame:
    """加载所有sheet"""
    dfs = pd.read_excel(file_path, engine="calamine", sheet_name=None)
    return dfs


def init_config() -> dict:
    """初始化config"""
    with open("./config/config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_keywords(keywords_path: str) -> str:
    """加载关键字，并进行转换"""
    content = ""
    with open(keywords_path, mode="r", encoding="utf-8") as f:
        content = f.read()
    return "|".join(content.strip().split())


def search_only(df: DataFrame, keywords: str, filter_columns: list) -> DataFrame:
    """查询关键字"""
    mask_list = []
    for column in filter_columns:
        if column in df.columns:
            result = (
                df[column]
                .fillna("")
                .astype(str)
                .str.contains(keywords, na=False, case=False)
            )
            mask_list.append(result)
    final_mask = functools.reduce(operator.or_, mask_list)

    return df[final_mask]


def search_add_keywords(
    df: DataFrame, keywords: str, filter_columns: list
) -> DataFrame:
    """查询关键字，并且添加匹配到的关键字"""
    match_df = search_only(df, keywords, filter_columns)

    if match_df.empty:
        return match_df

    all_match_list = pd.Series([[] for _ in range(len(match_df))], index=match_df.index)

    for column in filter_columns:
        if column in match_df.columns:
            all_match_list += match_df[column].fillna("").str.findall(keywords)

    def format_keywords(keyword_list: list) -> str:
        """格式化关键字列"""
        unique_keywords = {k.lower() for k in keyword_list}
        return " ".join(sorted(list(unique_keywords)))

    match_df["关键字"] = all_match_list.apply(format_keywords)
    return match_df


def save_excel(df: DataFrame) -> None:
    # 加载模板
    wb = load_workbook("./template/template.xlsx")
    ws = wb.active

    start_row = 2
    for index, row in df.iterrows():
        current_row = start_row + index

        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=current_row, column=col_idx, value=value)

    wb.save("./output/结果.xlsx")


def main():
    pass


if __name__ == "__main__":
    main()

import functools
import json
import logging
import operator
import time
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from pandas import DataFrame

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

console_handle = logging.StreamHandler()
console_handle.setLevel(logging.INFO)
console_handle.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

file_handle = logging.FileHandler(filename="./log/app.log", mode="a", encoding="utf-8")
file_handle.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
file_handle.setLevel(logging.DEBUG)

logger.addHandler(console_handle)
logger.addHandler(file_handle)


def load_folder(folder: str = r"./source") -> list:
    """加载目录"""

    file_folder = Path(folder)

    if not file_folder.exists():
        logger.error(f"路径不存在,请进行检查：{file_folder}")
        return None
    logger.info(f"正在加载路径目录：{folder}")
    exist_suffix = [".xlsx", ".xls"]

    excel_files = [
        file for file in file_folder.rglob("*") if file.suffix in exist_suffix
    ]
    if not excel_files:
        logger.warning(f"{file_folder}中没有找到excel文件")
        return

    logger.info(f"共找到{len(excel_files)}个excel文件,准备处理....")

    return excel_files


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


def search_excel(source_path: str, keywords: str, filter_columns: list):
    "使用关键字，对直接的列进行筛选"
    logger.info(f">>> 正在处理：{source_path.name}")
    dfs = pd.read_excel(source_path, engine="calamine", sheet_name=None)
    result_list = []

    for sheet_name, df in dfs.items():
        logger.info(f"  -> 正在读取工作表：{sheet_name}")
        final_list = []
        for coulumn in filter_columns:
            result = df[coulumn].astype(str).str.contains(keywords, na=False)
            final_list.append(result)

        final_serserl = functools.reduce(operator.or_, final_list)
        match_df = df[final_serserl]

        if not match_df.empty:
            logger.info(f"      - 工作表{sheet_name}中匹配{len(match_df)}行")

        else:
            logger.info(f"      - 工作表{sheet_name}没有匹配到")
        result_list.append(match_df)
    final_result = pd.concat(result_list, ignore_index=True)
    return final_result


def save_excel(df: DataFrame) -> None:
    # 加载模板
    wb = load_workbook("./template/template.xlsx")
    ws = wb.active

    start_row = 2
    for index, row in df.iterrows():
        current_row = start_row + index

        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=current_row, column=col_idx, value=value)

    wb.save("./结果.xlsx")


def search_or_keywords():
    all_matches_list = []
    start_time = time.time()
    # 1.加载所有文件夹中的所有文件excel路径
    logger.info("---系统启动---")

    logger.info("初始化配置中....")
    config = init_config()
    FILE_PATH = config.get("file_path")
    FILTER_COLUMNS = config.get("filter_columns")
    logger.info(f"处理目录：{FILE_PATH}")
    logger.info(f"处理列: {FILTER_COLUMNS}")

    source_path = load_folder(FILE_PATH)

    # 2.处理关键字
    keywords = get_keywords("./keywords.txt")
    logger.info("加载关键字中.....")
    # 3. 循环输入excel,进行筛选.

    for file_path in source_path:
        all_matches_list.append(search_excel(file_path, keywords, FILTER_COLUMNS))

    all_final_df = pd.concat(all_matches_list, ignore_index=True)
    # 4.将结果进行保存
    save_excel(df=all_final_df)

    logger.info(f"总耗时： {time.time() - start_time:.2f}秒")
    logger.info("---系统关闭---")


if __name__ == "__main__":
    main()

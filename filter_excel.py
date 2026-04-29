import functools
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


def load_folder(folder: str) -> list:
    """加载目录"""

    file_folder = Path(folder)

    if not file_folder.exists():
        logger.error(f"加载路径失败：{file_folder}")
        return None

    exist_suffix = [".xlsx", ".xls"]

    file_path = [file for file in file_folder.rglob("*") if file.suffix in exist_suffix]
    return file_path


def get_keywords(keywords_path: str) -> str:
    """加载关键字，并进行转换"""
    content = ""
    with open(keywords_path, mode="r", encoding="utf-8") as f:
        content = f.read()

    return "|".join(content.strip().split())


def search_excel(source_path: str, keywords: str):
    "使用关键字，对直接的列进行筛选"
    logger.info(f"准备处理：{source_path.name}")
    dfs = pd.read_excel(source_path, engine="calamine", sheet_name=None)
    result_list = []
    for sheet_name, df in dfs.items():
        logger.info(f"sheet_name={sheet_name}")

        title = df["标题"].astype(str).str.contains(keywords, na=False)
        content = df["摘要"].astype(str).str.contains(keywords, na=False)

        final_list = [title, content]
        final_serserl = functools.reduce(operator.or_, final_list)
        result_list.append(df[final_serserl])
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


def main():
    all_matches_list = []
    start_time = time.time()
    # 1.加载所有文件夹中的所有文件excel路径
    file_path = r""
    source_path = load_folder(file_path=r"./source")
    logger.info(f"source_path={source_path}")
    # 2.处理关键字
    keywords = get_keywords("./keywords.txt")
    logger.info("正在加载关键字中.....")
    # 3. 循环输入excel,进行筛选.

    for file_path in source_path:
        all_matches_list.append(search_excel(file_path, keywords))

    all_final_df = pd.concat(all_matches_list, ignore_index=True)
    # 4.将结果进行保存
    save_excel(df=all_final_df)
    logger.info(f"总耗时： {time.time() - start_time}秒")


if __name__ == "__main__":
    main()

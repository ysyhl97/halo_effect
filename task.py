import functools
import logging
import time

import pandas as pd

from filter_excel import (
    get_keywords,
    init_config,
    load_all_sheet,
    load_folder,
    save_excel,
)

logger = logging.getLogger(__name__)


def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(f"总耗时：{duration:.2f}秒")
        return result

    return wrapper


@timing_decorator
def search_task(search_function_name: callable) -> None:
    confing = init_config()
    FILE_PATH = confing.get("file_path")
    FILTER_COLUMNS = confing.get("filter_columns")
    KEYWORD_PATH = confing.get("keyword_path")

    source_path = load_folder(FILE_PATH)
    keywords = get_keywords(KEYWORD_PATH)

    logger.info("========配置========")
    logger.info(f"筛选列名:{FILTER_COLUMNS}")
    logger.info("===================")

    all_match_df = []
    for file_path in source_path:
        logger.info(f">>> 处理工作薄：{file_path.name}")
        for sheet_name, df in load_all_sheet(file_path).items():
            logger.info(f" -> 处理工作表：{sheet_name}")
            match_df = search_function_name(df, keywords, FILTER_COLUMNS)
            if match_df.empty:
                logger.info(f"   - 工作表[{sheet_name}]没有匹配到任何结果")
            else:
                logger.info(f"   - 工作表[{sheet_name}]共匹配到{len(match_df)}条")
            all_match_df.append(match_df)
    all_df = pd.concat(all_match_df, ignore_index=True)
    logger.info(f"共匹配{len(all_df)}条")
    save_excel(all_df)
    logger.info("结果保存完毕")

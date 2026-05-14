import functools
import logging
import time

import pandas as pd
from pandas import DataFrame

from filter_excel import (
    extract_statistics,
    format_statistics_text,
    get_keywords,
    init_config,
    load_all_sheet,
    load_and_merge_sheets,
    load_folder,
    save_excel,
)
from profile_detector import detect_profile

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


def generate_report_for_profile(
    df: DataFrame, profile_config: dict, shared_formats: dict
):
    """为一个DataFrame和其对应的Profile配置生成报告"""
    calculations = profile_config.get("calculations")
    if not calculations:
        logger.warning("Profile中没有定义'calculations',无法生成报告")
        return

    stats_raw_data = extract_statistics(df, calculations, profile_config)

    format_config = shared_formats.copy()
    format_config.update(profile_config.get("formats", {}))
    format_config["template"] = profile_config.get(
        "template", "Profile中未定义'template'"
    )

    report_text = format_statistics_text(stats_raw_data, format_config)
    print(report_text)


def statistic_task():
    """
        文本统计主函数
    - 统计dataframe数据，输出文本
    """
    config = init_config()

    format_profiles = config.get("format_profiles")
    shared_formats = config.get("shared_formats", {})
    file_path_root = config.get("file_path", ".")
    input_path = input("请输入地址：")
    if not format_profiles:
        logger.error("配置文件缺少'format_profiles'定义")
        return

    source_paths = load_folder(input_path)

    for file_path in source_paths:
        sheets = load_all_sheet(file_path)
        merge_df = load_and_merge_sheets(sheets)
        if merge_df is None:
            continue
        active_profile = detect_profile(merge_df, config.get("format_profiles", {}))

        if not active_profile:
            logger.warning("没有为当前文件找到适合的profile")
            continue

        logger.info(
            f"    -> 监测到格式： '{active_profile.get('name', '未命名profile')}'"
        )
        generate_report_for_profile(
            merge_df, active_profile, config.get("shared_formats", {})
        )

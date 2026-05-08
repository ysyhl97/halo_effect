import pandas as pd

from filter_excel import (
    get_keywords,
    init_config,
    load_all_sheet,
    load_folder,
    save_excel,
)


def search_task(search_function_name: callable) -> None:
    confing = init_config()
    FILE_PATH = confing.get("file_path")
    FILTER_COLUMNS = confing.get("filter_columns")
    KEYWORD_PATH = confing.get("keyword_path")

    source_path = load_folder(FILE_PATH)
    keywords = get_keywords(KEYWORD_PATH)

    all_match_df = []
    for file_path in source_path:
        for sheet_name, df in load_all_sheet(file_path).items():
            match_df = search_function_name(df, keywords, FILTER_COLUMNS)
            all_match_df.append(match_df)
    all_df = pd.concat(all_match_df, ignore_index=True)
    save_excel(all_df)

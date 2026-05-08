import logging.config

import yaml

from filter_excel import search_add_keywords, search_only
from task import search_task

with open("./config/logging_config.yaml", "r", encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)
logging.config.dictConfig(config_dict)


def main():
    while True:
        print("====功能选择====")
        print("1.筛选")
        print("2.筛选（加关键字）")
        print("9.退出系统：exit/quit")

        number = input("请输入你选择的编号：").lower()

        match number:
            case "1":
                print("开始执行筛选功能")
                search_task(search_only)
            case "2":
                print("开始执行筛选功能(添加关键字)")
                search_task(search_add_keywords)
            case "3":
                print("功能3")
            case "exit" | "quit":
                print("正在退出系统....")
                break
            case _:
                print(f"你输入的{number}不对，请重新输入对应的任务编号")


if __name__ == "__main__":
    main()

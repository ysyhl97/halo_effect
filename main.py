from task import search_keywords


def main():
    while True:
        print("====功能选择====")
        print("1.筛选（关键字或）")
        print("2.筛选（加关键字）")
        print("9.退出系统：exit/quit")

        number = input("请输入你选择的编号：").lower()

        match number:
            case "1":
                print("功能1")
                search_keywords()
            case "2":
                print("功能2")
            case "3":
                print("功能3")
            case "exit" | "quit":
                print("正在退出系统....")
                break
            case _:
                print(f"你输入的{number}不对，请重新输入对应的任务编号")


if __name__ == "__main__":
    main()

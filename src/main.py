"""
AutoClicker - 入口文件

双击此脚本或打包后的 exe 即可启动连点器。
"""

from gui import AutoClickerGUI


def main():
    app = AutoClickerGUI()
    app.run()


if __name__ == "__main__":
    main()

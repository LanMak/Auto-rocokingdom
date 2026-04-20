import logging

from config import CONFIG
from core.engine import Engine
from core.logger import setup_logging
from modes import MODE_REGISTRY


def main() -> None:
    setup_logging()

    print("\n请选择运行模式:")
    for key, cls in sorted(MODE_REGISTRY.items()):
        mode = cls()
        print(f"  {key}: {mode.label}")
    print("有问题或新功能建议请提 issue。如果这个项目对你有帮助，欢迎点个 Star 支持一下。")
    print("\n[提示] 脚本支持自适应分辨率，推荐使用 2K（2560x1600 或 2560x1440）以获得更高识别精度。")
    print("分辨率越低 Score 可能越低；若识别异常，可在当前分辨率下重截 templates 进行适配。")
    print('[提示] 逃跑模式使用物理点击，请确保"是"按钮露出且不被其他窗口遮挡。')

    choices = "/".join(sorted(MODE_REGISTRY.keys()))
    choice = input(f"请输入选项 ({choices}): ").strip()

    mode_cls = MODE_REGISTRY.get(choice, MODE_REGISTRY["1"])
    mode = mode_cls()
    logging.info("已选择模式: %s", mode.label)
    from core.logger import log_audit
    log_audit("模式已选择", 模式=mode.name)

    Engine(mode).run()


if __name__ == "__main__":
    main()

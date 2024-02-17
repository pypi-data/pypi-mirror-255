import os
import sys
from importlib import resources
from pathlib import Path

from loguru import logger


def detect_runtime_environment():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller로 패키징된 실행 파일의 경우
        return "pyinstaller"
    elif "site-packages" in str(Path(__file__).absolute()):
        return "poetry"
    else:
        # 위의 조건에 해당하지 않는 경우, 개발 중인 상태로 간주합니다.
        return "development"


def get_resource_filepath(fn, package_type=None):
    if package_type == "pyinstaller":
        return os.path.join(sys._MEIPASS, "resources", fn)
    elif package_type == "poetry":
        return resources.files("shortkey").joinpath("resources", fn)
    else:  # development = package_type is None
        return os.path.join(Path(__file__).parent, "resources", fn)


PACKAGE_TYPE = detect_runtime_environment()
logger.info(f"PACKAGE_TYPE:{PACKAGE_TYPE} -- path:{Path(__file__).absolute()}")
ICON_PATH = get_resource_filepath("icon.png", package_type=PACKAGE_TYPE)
KEY_PATH = get_resource_filepath("keys.json", package_type=PACKAGE_TYPE)

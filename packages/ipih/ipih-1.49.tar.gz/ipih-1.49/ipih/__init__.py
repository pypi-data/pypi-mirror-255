import sys
import os
import importlib.util
import platform


NAME: str = "ipih"
VERSION: str = "1.49"

PIH_MODULE_NAME: str = "pih"
FACADE_NAME: str = "facade"
BUILD_FOLDER_NAME: str = "build"
WINDOWS_SHARE_DOMAIN_NAME: str = "pih"
WINDOWS_SHARE_DOMAIN_ALIAS: str = "fmv"


def get_path(is_linux: bool = False) -> str:
    if is_linux:
        return f"//mnt/{FACADE_NAME}"
    return f"//{WINDOWS_SHARE_DOMAIN_NAME}/{FACADE_NAME}"


def import_pih() -> None:
    is_build: bool = (
        len(
            list(
                filter(
                    lambda item: item.find(f"{os.sep}{BUILD_FOLDER_NAME}{os.sep}")
                    != -1,
                    __path__,
                )
            )
        )
        > 0
    )
    if is_build:
        sys.path.append(
            f"//{WINDOWS_SHARE_DOMAIN_NAME}/{FACADE_NAME}/{BUILD_FOLDER_NAME}"
        )
    else:
        module_is_exists = importlib.util.find_spec(PIH_MODULE_NAME) is not None
        if not module_is_exists:
            sys.path.append(get_path(platform.system() == "Linux"))


import_pih()

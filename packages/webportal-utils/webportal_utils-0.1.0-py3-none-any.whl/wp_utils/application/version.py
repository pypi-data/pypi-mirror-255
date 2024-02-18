from typing import Tuple, Union


def make_version_info(version: str) -> Tuple[Union[int, str]]:
    return tuple(int(num) if num.isdigit() else num for num in version.replace("-", ".", 1).split("."))

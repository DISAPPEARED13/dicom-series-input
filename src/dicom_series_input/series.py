"""只按 SeriesInstanceUID 收集文件，不读取像素，不拆分同一 UID。"""

from collections.abc import Iterable
from pathlib import Path

import pydicom


def collect_series(
    input_path: str | Path,
    pattern: str = "*.dcm",
    series_uids: Iterable[str] | str | None = None,
) -> dict[str, list[Path]]:
    """返回 {SeriesInstanceUID: [文件路径, ...]}。

    input_path：递归搜索的目录，相对路径按当前工作目录解析。
    pattern：文件名匹配规则；假定匹配文件可作为 DICOM 读取。
    series_uids：None 或空集合表示所有序列；也可传单个 UID 或多个 UID。
    返回的路径按文件路径排序收集，切片空间排序留给后续像素读取阶段。
    没有匹配文件或指定 UID 不存在时返回空字典；读取错误直接向调用者传递。
    """
    # 1. 将输入目录解析成绝对路径。
    root = Path(input_path).resolve()

    # 2. 递归搜索文件，只读取序列 UID，按 UID 收集绝对文件路径。
    series: dict[str, list[Path]] = {}
    for path in sorted(root.rglob(pattern)):
        if path.is_file():
            header = pydicom.dcmread(
                path,
                stop_before_pixels=True,
                specific_tags=["SeriesInstanceUID"],
            )
            uid = str(header.SeriesInstanceUID)
            series.setdefault(uid, []).append(path)

    # 3. 有指定 UID 时筛选；否则返回全部序列。
    selected = {series_uids} if isinstance(series_uids, str) else set(series_uids or ())
    if selected:
        series = {uid: paths for uid, paths in series.items() if uid in selected}
    return series

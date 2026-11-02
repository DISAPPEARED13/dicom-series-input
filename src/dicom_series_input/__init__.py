"""DICOM 输入：解析路径、按序列 UID 收集、按指定 UID 筛选。"""

from .series import collect_series

__all__ = ["collect_series"]

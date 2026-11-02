# dicom-series-input

本地 DICOM 输入包，只有一个公开函数 `collect_series()`：

1. `Path(input_path).resolve()` 解析输入目录。
2. 递归匹配文件，只读取 `SeriesInstanceUID`，收集同一 UID 的文件路径。
3. 根据可选的 UID 参数筛选序列。

同一 UID 完整返回，不按方向、像素间距、尺寸、回波或位置间隔再分组。
没有列出序列的命令行模式，不读取或打印 `SeriesDescription`。
像素读取、切片排序、校正和写出由调用方完成。

## 安装和使用

```powershell
python -m pip install -e E:/N4/packages/dicom-series-input
python -m pip list
python -m pip show dicom-series-input
```

`-e` 是可编辑安装：修改本地 Python 源码后，新 Python 进程会使用修改后的代码。
安装名是 `dicom-series-input`，Python 导入名是 `dicom_series_input`。
安装对执行命令的 Python 环境生效；IDE 使用其他解释器时，需要在那个环境安装。

## Hello World

将下面保存为 `hello_dicom.py`，把 `input_dir` 换成自己的输入目录，然后运行 `python hello_dicom.py`。

```python
from dicom_series_input import collect_series

input_dir = r"E:\N4\TABFC\data2_origin\9360"
series = collect_series(input_dir, pattern="Temp*.dcm")

print("Hello, DICOM!")
print(f"共找到 {len(series)} 个序列")
```

普通 DICOM 文件可用 `pattern="*.dcm"`；原始和比较图混放时按实际文件名选择 `Temp*.dcm`。

## print 序列状态

接在 Hello World 代码后面即可。这里的“状态”指收集到的序列及文件数量，不代表算法处理已成功。

```python
# 最直接：查看整个字典（只包含 UID 和文件路径）。
print(series)

# 简洁汇总：序列数、总文件数、每个序列的文件数及首个文件。
total_files = sum(len(paths) for paths in series.values())
print(f"序列数: {len(series)}，文件总数: {total_files}")
for uid, paths in series.items():
    print(f"UID: {uid} | 文件数: {len(paths)}")
    print(f"  首个文件: {paths[0]}")
```

输出形式示例：

```text
Hello, DICOM!
共找到 2 个序列
序列数: 2，文件总数: 22
UID: 1.2.3.4 | 文件数: 11
  首个文件: E:\example\Temp0001.dcm
UID: 1.2.3.5 | 文件数: 11
  首个文件: E:\example\Temp0012.dcm
```

## 筛选后交给算法

后续 Python DICOM 序列处理统一先调用此包，再把每个 UID 的 `paths` 交给任务自己的像素读取、空间排序和算法处理函数。
包负责收集文件路径，不把文件路径直接变成像素数组。

```python
from dicom_series_input import collect_series

series = collect_series("E:/N4/data", pattern="Temp*.dcm")
selected = collect_series("E:/N4/data", series_uids="1.2.3.4")
# 也可以传 series_uids=[uid_a, uid_b]。

for uid, paths in series.items():
    print(uid, len(paths))
    # 把 paths 交给自己的像素读取或算法函数。
```

`series_uids=None` 或空集合表示全部。返回类型是 `dict[str, list[pathlib.Path]]`。
返回路径是绝对路径，收集顺序是文件路径顺序，空间排序由调用方处理。
假定匹配文件可作为 DICOM 读取且有 `SeriesInstanceUID`；读取错误由 pydicom 直接抛出。
没有匹配结果时返回空字典；指定不存在的 UID 不会自动选择其他序列。

## 普通 Python 文件如何成为可安装包

```text
dicom-series-input/
├── pyproject.toml               # 安装名、版本、依赖、构建工具、源码位置
├── README.md                    # 使用说明
└── src/
    └── dicom_series_input/
        ├── __init__.py          # 导出 collect_series
        └── series.py            # 函数实现
```

将复用逻辑放进函数，参数通过函数传入，结果通过返回值交出。
导入时只定义函数，不自动扫描文件、运行算法或删除目录。
`pyproject.toml` 声明项目名称、版本、Python 要求、第三方依赖和构建后端。
pip 安装后会登记发行包元数据，因此能在 `pip list` 看到。

普通本地安装：`python -m pip install E:/N4/packages/dicom-series-input`。
生成 wheel：`python -m pip wheel --no-deps E:/N4/packages/dicom-series-input -w E:/N4/packages/dicom-series-input/dist`。
wheel 可复制到其他电脑，用 `python -m pip install <文件名.whl>` 安装。
本地安装和分发 wheel 都不需要上传 PyPI。

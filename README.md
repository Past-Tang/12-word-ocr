<div align="center">
  <img src="assets/logo.svg" alt="12-Word OCR Tool" width="680"/>

  # 12-Word OCR Tool

  **助记词图片 OCR 批量识别工具**

  [![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![PaddleOCR](https://img.shields.io/badge/PaddleOCR-Engine-2532d8?style=flat-square)](https://github.com/PaddlePaddle/PaddleOCR)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
</div>

---

## 项目概述

12-Word OCR Tool 是一个基于 PaddleOCR 引擎的助记词图片批量识别工具。程序自动扫描图片中的 12 个英文单词，通过智能网格排序算法将识别结果按正确顺序排列，最终导出为标准 CSV 文件。适用于需要从截图中批量提取 12 位助记词的场景。

## 技术栈

- **Python**: 核心编程语言
- **PaddleOCR**: OCR 识别引擎（通过 `PPOCR_api` 封装调用）
- **CSV**: 结果导出格式
- **正则表达式**: 文本过滤与清洗

## 功能特性

- **PaddleOCR 引擎** -- 高精度英文文本识别，支持自定义英文模型 (`config_en.txt`)
- **智能网格排序** -- 自动检测 3x4 网格布局，基于坐标中心点进行列优先/行优先排列
- **矩阵转置** -- 支持将列优先读取的结果转置为行优先顺序，确保助记词顺序正确
- **批量处理** -- 自动扫描 `image` 目录下所有 JPG/PNG/BMP 图片文件
- **智能过滤** -- 自动过滤包含数字的文本、中文字符和低置信度（<0.75）结果
- **CSV 导出** -- 识别结果自动保存为带时间戳的 CSV 文件，使用 `|` 分隔 12 个单词
- **异常标记** -- 当识别结果不足 12 个单词时自动标记为"异常"

## 安装说明

1. 克隆仓库到本地：
   ```bash
   git clone https://github.com/Past-Tang/12-word-ocr.git
   cd 12-word-ocr
   ```

2. 确保 OCR 引擎就绪：
   - `lib/model.exe` -- PaddleOCR 引擎可执行文件
   - `lib/models/config_en.txt` -- 英文模型配置文件

3. 无需额外安装 Python 依赖（OCR 引擎为独立可执行文件）

## 使用方法

1. 将待识别的助记词截图放入 `image` 目录（支持 `.jpg`、`.jpeg`、`.png`、`.bmp`）
2. 运行启动脚本或直接执行主程序：
   ```bash
   # 方式一：使用启动脚本
   ./run.ps1

   # 方式二：直接运行
   python main/main.py
   ```
3. 程序自动执行流程：
   - 初始化 OCR 引擎并加载英文模型
   - 逐张扫描 `image` 目录下的图片
   - 对每张图片执行：OCR 识别 -> 文本过滤 -> 网格排序 -> 矩阵转置
   - 将结果保存为 `ocr_results_<timestamp>.csv`

## 配置参数

在 `main/main.py` 的 `main()` 函数中可调整以下参数：

| 参数 | 默认值 | 说明 |
|:---|:---|:---|
| `USE_ENGLISH_MODEL` | `True` | 是否使用英文识别模型 |
| `REMOVE_NUMBERS` | `True` | 是否过滤包含数字的识别结果 |
| `MIN_CONFIDENCE` | `0.75` | 最低置信度阈值，低于此值的结果将被丢弃 |
| `TRANSPOSE` | `True` | 是否对网格结果进行矩阵转置 |
| `GRID_ROWS` | `3` | 助记词网格行数 |
| `GRID_COLS` | `4` | 助记词网格列数 |

## 项目结构

```
12-word-ocr/
├── main/
│   ├── main.py          # 主程序：OCR 识别、过滤、排序、导出
│   └── PPOCR_api.py     # PaddleOCR API 封装层
├── lib/
│   ├── model.exe        # PaddleOCR 引擎可执行文件
│   └── models/          # 模型文件目录
│       └── config_en.txt  # 英文模型配置
├── image/               # 待识别图片目录（用户放入截图）
├── assets/
│   └── logo.svg         # 项目 Logo
├── run.ps1              # PowerShell 启动脚本
├── LICENSE              # MIT 许可证
└── README.md
```

## 核心算法

### 网格排序 (`sort_blocks_grid`)
1. 计算每个文本块的坐标中心点 `(x_center, y_center)`
2. 列优先模式：先按 X 坐标排序分列（阈值 100px），每列内按 Y 坐标排序
3. 行优先模式：先按 Y 坐标排序分行（阈值 50px），每行内按 X 坐标排序

### 矩阵转置 (`transpose_list`)
将 3x4 列优先读取的结果转换为行优先顺序，确保助记词按 1-12 正确排列。

## 输出格式

CSV 文件包含两列：
- **文件名**: 原始图片文件名
- **识别文本**: 12 个单词以 `|` 分隔，或标记为"异常"

```csv
文件名,识别文本
image_001.png,abandon|ability|able|about|above|absent|absorb|abstract|absurd|abuse|access|accident
image_002.png,异常
```

## 常见问题

### OCR 引擎启动失败？
确保 `lib/model.exe` 存在且路径正确。程序会自动检测引擎路径。

### 识别结果顺序不对？
调整 `TRANSPOSE` 参数。设为 `True` 时会对 3x4 网格进行矩阵转置。

### 识别结果不足 12 个？
检查图片质量，或降低 `MIN_CONFIDENCE` 阈值（默认 0.75）。

## 安全注意事项

- 助记词是加密资产的核心凭证，请在安全环境下使用本工具
- 处理完成后及时删除 `image` 目录中的截图和生成的 CSV 文件
- 请勿将包含助记词的文件上传到任何在线服务

## 许可证

[MIT License](LICENSE)

## 免责声明

本工具仅供学习研究使用，请勿用于任何非法用途。使用者需自行承担所有风险与责任。
# AlphaBetter — 蛋白质结构稳定性分析与 3D 可视化平台

## 项目简介

AlphaBetter 是一个蛋白质结构稳定性分析工具。输入一个 PDB 文件，自动完成：

1. **二级结构识别**：优先读取 PDB 自带的 HELIX/SHEET 注释；若无注释，使用基于几何/氢键规则的 USSA 方法自动识别。
2. **残基级稳定性打分**：基于二肽和五肽参考数据库，对每个残基输出稳定性评分（正值=稳定，负值=不稳定）。
3. **3D 可视化**：Web 界面以卡通图（cartoon）展示蛋白质结构，按评分着色（绿=稳定，黄=中性，红=不稳定）。
4. **结果导出**：输出带 B-factor 评分的彩色 PDB 文件，可在 PyMOL/ChimeraX 中查看。

## 环境要求

- Python >= 3.10
- numpy
- FastAPI + uvicorn（Web 服务用）
- python-multipart（文件上传用）

安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 方式一：命令行一键预测（推荐用于评测）

```bash
python predict.py --input test.pdb --output results/
```

输出文件：
- `results/residue_scores.csv` — 每个残基的稳定性评分
- `results/hits.csv` — 命中数据库的二肽/五肽片段
- `results/colored_test.pdb` — 带 B-factor 着色的 PDB
- `results/summary.csv` — 汇总统计

### 方式二：Jupyter Notebook

```bash
cd notebooks/
jupyter notebook demo.ipynb
```

### 方式三：Web 界面（可选）

```bash
# 先构建前端（需要 Node.js）
cd frontend/
npm install
npm run build
cd ..

# 启动后端
uvicorn app:app --host 0.0.0.0 --port 8765
```

浏览器打开 `http://localhost:8765`，上传 PDB 文件即可。

## 目录结构

```
├── README.md               # 本文件
├── requirements.txt       # Python 依赖
├── predict.py              # 主运行入口（命令行）
├── calc_stability.py       # 核心计算：二级结构识别 + 稳定性打分
├── utils.py                # 工具函数：B-factor 写入、评分读取
├── app.py                  # FastAPI Web 后端（可选）
├── data/
│   ├── db_dipeptides.csv   # 二肽参考数据库（389 条）
│   ├── db_pentapeptides.csv # 五肽参考数据库（40656 条）
│   └── README.md           # 数据说明
├── notebooks/
│   └── demo.ipynb          # 演示 Notebook
├── models/
│   └── README.md           # 模型说明（本项目为传统方法，无训练权重）
├── results/                # 运行输出目录
├── frontend/               # React Web 前端
├── Dockerfile              # Docker 部署
└── test.pdb                # 示例输入（溶菌酶 1AKI）
```

## 算法说明

### 二级结构识别

1. 优先读取 PDB 文件中的 `HELIX` 和 `SHEET` 记录行。
2. 若无注释，则使用 USSA 风格方法：
   - 为缺氢残基补 N-H 氢原子位置
   - 计算主链氢键（E = 27.888 × (1/ON + 1/CH - 1/OH - 1/CN)）
   - 根据 i,i+4 / i,i+3 / i,i+5 氢键模式识别 α/3-10/π 螺旋
   - 根据连续 beta bridge 识别折叠片
3. 最终将二级结构映射为 H（螺旋）、E（折叠）、C（无规卷曲）三类。

### 稳定性打分

- **二肽打分**：对于连续两个同二级结构的残基（H-H 或 E-E），在二肽数据库中查找对应氨基酸对的评分。
- **五肽打分**：对于连续五个同二级结构的残基，在五肽数据库中查找对应五肽序列的评分。
- 每个残基的最终得分为其参与的所有二肽/五肽命中之和。
- 正值表示稳定，负值表示不稳定，绝对值大小表示程度。

### 数据来源

二肽和五肽数据库基于蛋白质热稳定性实验数据构建，包含二肽/五肽序列、二级结构类型和热力学评分。详见 `data/README.md`。

## 第三方依赖

| 组件 | 版本 | 用途 | 许可 |
|------|------|------|------|
| numpy | 2.4.6 | 数值计算 | BSD-3 |
| FastAPI | 0.141.1 | Web 后端 | MIT |
| NGL.js | 2.0.0-dev.37 | 3D 分子可视化（前端） | MIT |

## 创新点

1. 无需深度学习模型，纯几何+数据库方法即可快速预测残基级稳定性。
2. 二级结构识别有双保险（PDB 注释 + USSA 几何推断），兼容无注释 PDB。
3. 输出 B-factor 着色 PDB，可直接导入 PyMOL 等工具查看。
4. 提供 Web 界面，支持拖拽上传和实时 3D 交互。

#!/usr/bin/env python3
"""
AlphaBetter — 蛋白质结构稳定性一键预测入口

用法:
    python predict.py --input test.pdb --output results/

输入:
    --input   输入 PDB 文件路径（必需）
    --output  输出目录（默认 results/）

输出:
    results/residue_scores.csv    每个残基的稳定性评分
    results/hits.csv              命中二肽/五肽数据库的片段
    results/colored_*.pdb         带 B-factor 评分的彩色 PDB
    results/summary.csv           汇总统计
"""

import argparse
import sys
from pathlib import Path

# 项目根目录加入路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from calc_stability import calc_stability
from utils import read_residue_scores, write_b_factor


def main():
    parser = argparse.ArgumentParser(
        description="AlphaBetter: 蛋白质结构稳定性分析"
    )
    parser.add_argument("--input", required=True, help="输入 PDB 文件路径")
    parser.add_argument(
        "--output", default="results", help="输出目录（默认 results/）"
    )
    args = parser.parse_args()

    pdb_path = Path(args.input).resolve()
    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    di_db = BASE_DIR / "data" / "db_dipeptides.csv"
    penta_db = BASE_DIR / "data" / "db_pentapeptides.csv"

    if not pdb_path.exists():
        print(f"[ERROR] PDB 文件不存在: {pdb_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] 输入 PDB: {pdb_path}")
    print(f"[INFO] 输出目录: {out_dir}")

    # 1. 计算稳定性分数
    print("[INFO] 正在计算稳定性分数...")
    calc_stability(
        pdb_file=str(pdb_path),
        di_csv=str(di_db),
        penta_csv=str(penta_db),
        out_dir=str(out_dir),
    )
    score_csv = out_dir / "residue_scores.csv"

    # 2. 读取评分并写入 B-factor
    print("[INFO] 生成彩色 PDB...")
    score_map = read_residue_scores(score_csv)
    colored_pdb = out_dir / f"colored_{pdb_path.name}"
    matched = write_b_factor(pdb_path, colored_pdb, score_map)
    print(f"[INFO] 匹配残基数: {matched}")

    # 3. 生成汇总统计
    print("[INFO] 生成汇总...")
    scores = list(score_map.values())
    if scores:
        positive = sum(1 for s in scores if s > 0.05)
        negative = sum(1 for s in scores if s < -0.05)
        neutral = len(scores) - positive - negative
        min_s = min(scores)
        max_s = max(scores)
    else:
        positive = negative = neutral = 0
        min_s = max_s = 0.0

    summary_path = out_dir / "summary.csv"
    with summary_path.open("w", encoding="utf-8-sig") as f:
        f.write("指标,值\n")
        f.write(f"总残基数,{len(scores)}\n")
        f.write(f"稳定区域(评分>0.05),{positive}\n")
        f.write(f"不稳定区域(评分<-0.05),{negative}\n")
        f.write(f"中性区域,{neutral}\n")
        f.write(f"最低评分,{min_s:.4f}\n")
        f.write(f"最高评分,{max_s:.4f}\n")

    print(f"[DONE] 汇总: {summary_path}")
    print(f"[DONE] 彩色 PDB: {colored_pdb}")
    print(f"[DONE] 残基评分: {score_csv}")
    print("[SUCCESS] 全部完成！")


if __name__ == "__main__":
    main()

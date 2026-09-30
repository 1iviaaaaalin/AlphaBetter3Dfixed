#!/bin/bash
# AlphaBetter 一键运行脚本
# 用法: bash run.sh <input.pdb> [output_dir]

set -e

INPUT="${1:-test.pdb}"
OUTPUT="${2:-results}"

echo "=== AlphaBetter 蛋白质稳定性分析 ==="
echo "输入: $INPUT"
echo "输出: $OUTPUT"
echo ""

python3 predict.py --input "$INPUT" --output "$OUTPUT"

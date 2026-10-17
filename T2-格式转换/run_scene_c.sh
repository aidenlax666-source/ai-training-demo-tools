#!/usr/bin/env bash
# 场景C 批量重命名（课堂精讲独立入口）
# 不调用任何大模型 API。
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "==> 创建虚拟环境 .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> 安装依赖（课前若已预装会很快）"
pip install -r requirements.txt -q

echo "==> 清空并重建 samples/output/scene_c"
rm -rf "samples/output/scene_c"
mkdir -p "samples/output/scene_c"

echo "==> 执行：场景C 批量重命名"
python format_batch.py --config config.scene_c.yaml

echo ""
echo "==> 输出（samples/output/scene_c）："
ls -la "samples/output/scene_c" || true
echo "场景完成。"

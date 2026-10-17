#!/usr/bin/env bash
# 场景A CSV↔Excel（课堂精讲独立入口）
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

echo "==> 清空并重建 samples/output/scene_a"
rm -rf "samples/output/scene_a"
mkdir -p "samples/output/scene_a"

echo "==> 执行：场景A CSV↔Excel"
python format_batch.py --config config.scene_a.yaml

echo ""
echo "==> 输出（samples/output/scene_a）："
ls -la "samples/output/scene_a" || true
echo "场景完成。"

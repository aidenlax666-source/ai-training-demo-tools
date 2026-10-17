#!/usr/bin/env bash
# T2 最小一键演示（默认 config.demo-minimal.yaml：CSV→Excel + 可选重命名）
# 三种课堂精讲场景请用：run_scene_a.sh / run_scene_b.sh / run_scene_c.sh
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

if [[ ! -f config.demo-minimal.yaml ]]; then
  echo "[错误] 缺少 config.demo-minimal.yaml"
  exit 1
fi
cp -f config.demo-minimal.yaml config.yaml

echo "==> 清空并重建 samples/output（不影响 scene_a/b/c 子目录外的精讲样例结构）"
# 只清 output 根下的文件，保留 scene_* 子目录内容由各 scene 脚本自己管
mkdir -p samples/output
find samples/output -maxdepth 1 -type f -delete 2>/dev/null || true

echo "==> 执行最小演示（CSV→Excel + 可选 rename）"
python format_batch.py --config config.demo-minimal.yaml

echo ""
echo "==> 输出目录（samples/output/）文件列表："
ls -la samples/output || true
echo ""
echo "最小演示完成。三种精讲场景请分别运行："
echo "  bash run_scene_a.sh   # CSV↔Excel"
echo "  bash run_scene_b.sh   # GBK→UTF-8"
echo "  bash run_scene_c.sh   # 批量重命名"
echo "或一次跑三种：依次执行上面三条；Windows 用对应 .bat"

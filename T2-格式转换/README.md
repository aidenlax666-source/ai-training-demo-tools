# T2：固定格式转换 / 文件批量处理

> **一句话**：把「每次让 AI 改文件格式」变成「一次写好配置，以后拖进文件夹就自动转」。
>
> **重要**：本流程**纯本地规则处理，不调用任何大模型 API**。

---

## 课前准备（强烈建议）

1. 已安装 Python 3.9+（Windows 安装时勾选 Add to PATH）  
2. **课前预装依赖**（避免现场弱网卡在 `pip`）：
   ```bash
   # 先进入本文件夹，再执行：
   python3 -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 依赖：`pandas`、`openpyxl`、`PyYAML`（见 `requirements.txt`）

---

## 怎么运行（macOS/Linux vs Windows）

| 用途 | macOS / Linux | Windows |
|------|---------------|---------|
| **最小演示**（CSV→Excel + 可选重命名） | `bash run_demo.sh` | 双击 `run_demo.bat` |
| 场景 A CSV↔Excel | `bash run_scene_a.sh` | 双击 `run_scene_a.bat` |
| 场景 B GBK→UTF-8 | `bash run_scene_b.sh` | 双击 `run_scene_b.bat` |
| 场景 C 批量重命名 | `bash run_scene_c.sh` | 双击 `run_scene_c.bat` |
| 手动指定配置 | `python format_batch.py --config …` | 同上（先 activate） |
| 只预览不写文件 | 加 `--dry-run` | 加 `--dry-run` |

**先进入本文件夹**再执行上述命令（不要依赖机房绝对路径）。

---

## 配置怎么选

| 文件 | 用途 |
|------|------|
| `config.demo-minimal.yaml` | **默认最小**：仅 csv→xlsx（+可选 rename）。`run_demo` 用它 |
| `config.example.full.yaml` | 完整四 job 进阶示例（第二节课再打开） |
| `config.scene_a.yaml` | 课堂精讲 A |
| `config.scene_b.yaml` | 课堂精讲 B |
| `config.scene_c.yaml` | 课堂精讲 C |
| `config.example.yaml` | 模板说明；没有 `config.yaml` 时可复制 |

---

## 场景 A：CSV ↔ Excel

**解决什么**：同事甩 CSV / 系统要 CSV。

**命令**：`bash run_scene_a.sh` 或 `run_scene_a.bat`

| 输入 | 输出 |
|------|------|
| `samples/input/scene_a/employees.csv` | `samples/output/scene_a/employees.xlsx` |
| `samples/input/scene_a/products.csv` | `samples/output/scene_a/products.xlsx` |
| `samples/input/scene_a/inventory.xlsx` | `samples/output/scene_a/inventory.csv` |

**课堂讲法**：打开 `config.scene_a.yaml` 看 `from/to/pattern` → 跑脚本 → 打开 xlsx/csv。  
**改成自己的（一句）**：改 `input_dir`/`output_dir`/`pattern`。

---

## 场景 B：GBK → UTF-8

**解决什么**：Windows GBK 文件在别处打开乱码。

**命令**：`bash run_scene_b.sh` 或 `run_scene_b.bat`

| 输入（GBK） | 输出（UTF-8） |
|-------------|---------------|
| `samples/input/scene_b/meeting_notes_gbk.txt` | `samples/output/scene_b/meeting_notes_utf8.txt` |
| `samples/input/scene_b/orders_gbk.csv` | `samples/output/scene_b/orders_utf8.csv` |

**验证乱码→正常**：

```bash
# 错编码打开源文件（会乱码）
python3 -c "print(open('samples/input/scene_b/meeting_notes_gbk.txt','rb').read().decode('utf-8','replace'))"
# 打开转换结果（应正常中文）
cat samples/output/scene_b/meeting_notes_utf8.txt
```

**改成自己的（一句）**：改 `from_encoding`/`to_encoding`/`pattern`。

---

## 场景 C：批量重命名

**解决什么**：统一「归档_001_…」命名。

**命令**：`bash run_scene_c.sh` 或 `run_scene_c.bat`（每次清空本场景输出，避免干扰）

| 输入 | 输出（示例，序号按文件名排序） |
|------|--------------------------------|
| `samples/input/scene_c/*.txt` | `samples/output/scene_c/归档_00N_….txt` |

**改成自己的（一句）**：改 `prefix`/`sequence`/`sequence_start`。

---

## 最小演示从哪到哪

`run_demo` 使用根目录样例 `samples/input/*.csv` → `samples/output/`（xlsx，并可选 `导出_00N_` 前缀）。  
若源文件名含 `_gbk`，转成 xlsx 时会**去掉文件名中的 `_gbk`**（内容已正确读取），避免误以为「还是乱码文件」。

---

## dry-run 与 rename 注意

```bash
python format_batch.py --config config.demo-minimal.yaml --dry-run
```

- dry-run **不写文件**，只打印 `[预览]`。  
- **rename 预览基于当前 output 实况**：若上次已生成带「导出_」的文件，会提示「均已带前缀」。正式演示请先跑 `run_demo`（会清 output 根下旧文件）或先清空输出再 dry-run。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| pip 超时 / 很慢 | **课前预装**；换镜像如 `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 找不到配置 | 确认已进入本文件夹；或 `run_demo` 会使用 `config.demo-minimal.yaml` |
| 无匹配文件 | 检查 `pattern` 与输入目录 |
| Windows 不会 bash | 用对应的 `.bat` |
| 缺少 pandas | `pip install -r requirements.txt` |

---

## 相关文档

- [`课堂演示要点.md`](./课堂演示要点.md) — A/B/C 各 3～5 分钟手把手  
- [`改成自己的.md`](./改成自己的.md) — 三种场景最短改造 + Windows 路径  
- [`提示词.md`](./提示词.md) — 用 AI 生成同类脚本（生成后仍不调 API）

---

## 三句自检（课程铁律）

1. **零安装 / 少安装？** — 只需 Python + 三个 pip 包；无云端、无账号。  
2. **改 3 处能否变自己的？** — 路径、`pattern`、前缀/编码，见 `改成自己的.md`。  
3. **有没有多余大框架？** — 无 GUI、无数据库、无 LLM；默认最小 jobs，完整能力进阶再开。

---

*培训项目 T2 成品包 · 不调用大模型 API*

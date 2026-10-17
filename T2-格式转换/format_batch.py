#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T2：固定格式转换 / 文件批量处理脚本
====================================
一次配置（config.yaml）、长期使用。纯本地规则处理，不调用任何大模型 API。

用法：
  python format_batch.py --config config.yaml
  python format_batch.py --config config.yaml --dry-run

支持任务类型：
  convert  — CSV ↔ XLSX 互转
  encoding — 文本/CSV 编码转换（如 gbk → utf-8）
  rename   — 固定规则批量重命名（前缀/后缀/序号）
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 依赖检查（给学员友好提示）
# ---------------------------------------------------------------------------
try:
    import yaml
except ImportError:
    print("[错误] 缺少 PyYAML。请先执行: pip install -r requirements.txt")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("[错误] 缺少 pandas。请先执行: pip install -r requirements.txt")
    sys.exit(1)


# ========================= 工具函数 =========================

def log_ok(msg: str) -> None:
    print(f"  [成功] {msg}")


def log_fail(msg: str) -> None:
    print(f"  [失败] {msg}")


def log_info(msg: str) -> None:
    print(f"  [信息] {msg}")


def log_skip(msg: str) -> None:
    print(f"  [跳过] {msg}")


def ensure_dir(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def match_files(directory: Path, pattern: str) -> list[Path]:
    """按 glob 模式匹配文件（不含子目录递归，保持路径简单可预期）。"""
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob(pattern) if p.is_file())


def read_text_with_encodings(path: Path, encodings: list[str]) -> tuple[str, str]:
    """依次尝试编码列表，返回 (文本, 实际编码)。"""
    last_err: Exception | None = None
    for enc in encodings:
        try:
            return path.read_text(encoding=enc), enc
        except (UnicodeDecodeError, LookupError) as e:
            last_err = e
    raise last_err or UnicodeDecodeError("unknown", b"", 0, 1, "无法解码")


def resolve_csv_encoding(path: Path, configured: str | None) -> str:
    """配置为 auto 时先 utf-8 再 gbk；否则用指定编码。"""
    if not configured or configured.lower() == "auto":
        try:
            path.read_text(encoding="utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            return "gbk"
    return configured


# ========================= 任务：convert =========================

def job_convert(
    job: dict[str, Any],
    input_dir: Path,
    output_dir: Path,
    dry_run: bool,
) -> tuple[int, int]:
    """CSV ↔ XLSX 批量互转。返回 (成功数, 失败数)。"""
    from_fmt = str(job.get("from", "")).lower()
    to_fmt = str(job.get("to", "")).lower()
    pattern = job.get("pattern") or f"*.{from_fmt}"
    delimiter = job.get("delimiter", ",")
    sheet_name = job.get("sheet_name", "Sheet1")
    header = bool(job.get("header", True))
    encoding_cfg = job.get("encoding", "auto")

    ok, fail = 0, 0
    files = match_files(input_dir, pattern)
    if not files:
        log_info(f"无匹配文件：{input_dir}/{pattern}")
        return 0, 0

    ensure_dir(output_dir, dry_run)

    for src in files:
        try:
            if from_fmt == "csv" and to_fmt == "xlsx":
                enc = resolve_csv_encoding(src, encoding_cfg)
                df = pd.read_csv(
                    src,
                    sep=delimiter,
                    encoding=enc,
                    header=0 if header else None,
                )
                # 文件名含 _gbk 时去掉标记，避免输出仍叫 orders_gbk.xlsx 造成「还是乱码」误解
                out_stem = src.stem
                if "_gbk" in out_stem.lower():
                    out_stem = (
                        out_stem.replace("_gbk", "")
                        .replace("_GBK", "")
                        .replace("_Gbk", "")
                    )
                    if not out_stem:
                        out_stem = src.stem
                    note = f"；内容已按 {enc} 正确读取，输出名去掉 _gbk"
                else:
                    note = ""
                out = output_dir / (out_stem + ".xlsx")
                if dry_run:
                    log_info(
                        f"[预览] {src.name} → {out.name} (encoding={enc}, rows={len(df)}{note})"
                    )
                else:
                    df.to_excel(out, index=False, sheet_name=sheet_name, engine="openpyxl")
                    log_ok(
                        f"{src.name} → {out.name} ({len(df)} 行, encoding={enc}{note})"
                    )
                ok += 1

            elif from_fmt == "xlsx" and to_fmt == "csv":
                df = pd.read_excel(
                    src,
                    sheet_name=sheet_name if sheet_name else 0,
                    header=0 if header else None,
                    engine="openpyxl",
                )
                out = output_dir / (src.stem + ".csv")
                if dry_run:
                    log_info(f"[预览] {src.name} → {out.name} (rows={len(df)})")
                else:
                    df.to_csv(out, index=False, sep=delimiter, encoding="utf-8-sig")
                    log_ok(f"{src.name} → {out.name} ({len(df)} 行)")
                ok += 1

            else:
                log_fail(f"{src.name}: 不支持的转换 {from_fmt} → {to_fmt}（仅支持 csv↔xlsx）")
                fail += 1

        except Exception as e:
            log_fail(f"{src.name}: {e}")
            fail += 1

    return ok, fail


# ========================= 任务：encoding =========================

def job_encoding(
    job: dict[str, Any],
    input_dir: Path,
    output_dir: Path,
    dry_run: bool,
) -> tuple[int, int]:
    """文本编码批量转换。返回 (成功数, 失败数)。"""
    from_enc = job.get("from_encoding", "gbk")
    to_enc = job.get("to_encoding", "utf-8")
    pattern = job.get("pattern", "*.txt")

    ok, fail = 0, 0
    files = match_files(input_dir, pattern)
    if not files:
        log_info(f"无匹配文件：{input_dir}/{pattern}")
        return 0, 0

    ensure_dir(output_dir, dry_run)

    for src in files:
        try:
            text, used = read_text_with_encodings(src, [from_enc, "gbk", "gb2312", "utf-8"])
            out_name = src.name
            # 若文件名暗示 gbk，转换后可去掉标记，便于识别
            if "_gbk" in src.stem.lower() and to_enc.lower().startswith("utf"):
                out_name = src.stem.replace("_gbk", "").replace("_GBK", "") + "_utf8" + src.suffix
            out = output_dir / out_name

            if dry_run:
                log_info(f"[预览] {src.name} ({used}) → {out.name} ({to_enc})")
            else:
                out.write_text(text, encoding=to_enc)
                log_ok(f"{src.name} ({used}) → {out.name} ({to_enc})")
            ok += 1
        except Exception as e:
            log_fail(f"{src.name}: {e}")
            fail += 1

    return ok, fail


# ========================= 任务：rename =========================

def job_rename(
    job: dict[str, Any],
    input_dir: Path,
    output_dir: Path,
    dry_run: bool,
) -> tuple[int, int]:
    """
    固定规则批量重命名，并输出到 output_dir。
    source: input → 从输入目录复制并改名
            output → 对输出目录已有文件改名（转完再改名的典型场景）
    """
    pattern = job.get("pattern", "*")
    prefix = job.get("prefix", "") or ""
    suffix = job.get("suffix", "") or ""
    sequence = bool(job.get("sequence", False))
    seq_start = int(job.get("sequence_start", 1))
    source = str(job.get("source", "output")).lower()

    src_dir = input_dir if source == "input" else output_dir
    files = match_files(src_dir, pattern)
    if not files:
        log_info(f"无匹配文件：{src_dir}/{pattern}")
        return 0, 0

    ensure_dir(output_dir, dry_run)
    ok, fail = 0, 0

    # 已带目标前缀的文件跳过，避免重复跑时叠成「导出_001_导出_001_…」
    if prefix:
        files = [p for p in files if not p.name.startswith(prefix)]
        if not files:
            log_info(f"匹配文件均已带前缀「{prefix}」，无需重命名")
            return 0, 0

    for i, src in enumerate(files):
        try:
            seq_part = f"{seq_start + i:03d}_" if sequence else ""
            new_name = f"{prefix}{seq_part}{src.stem}{suffix}{src.suffix}"
            dest = output_dir / new_name

            if dest.resolve() == src.resolve():
                log_skip(f"{src.name}: 新旧名相同，无需处理")
                ok += 1
                continue

            if dry_run:
                log_info(f"[预览] {src.name} → {new_name}")
            else:
                # 同源目录改名用 rename；跨目录或需保留原文件则 copy
                if src.parent.resolve() == output_dir.resolve():
                    src.rename(dest)
                else:
                    shutil.copy2(src, dest)
                log_ok(f"{src.name} → {new_name}")
            ok += 1
        except Exception as e:
            log_fail(f"{src.name}: {e}")
            fail += 1

    return ok, fail


# ========================= 主流程 =========================

JOB_HANDLERS = {
    "convert": job_convert,
    "encoding": job_encoding,
    "rename": job_rename,
}


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("配置文件根节点必须是 YAML 映射（字典）")
    return data


def run(config_path: Path, dry_run: bool) -> int:
    print("=" * 60)
    print("T2 格式批量处理（纯本地规则，不调用大模型 API）")
    if dry_run:
        print("【DRY-RUN 模式】只预览，不写入任何文件")
    print("=" * 60)

    try:
        cfg = load_config(config_path)
    except Exception as e:
        print(f"[错误] 无法读取配置 {config_path}: {e}")
        return 1

    # 路径相对「配置文件所在目录」，方便任意工作目录调用
    base = config_path.resolve().parent
    input_dir = (base / str(cfg.get("input_dir", "samples/input"))).resolve()
    output_dir = (base / str(cfg.get("output_dir", "samples/output"))).resolve()
    jobs = cfg.get("jobs") or []

    print(f"配置文件 : {config_path}")
    print(f"输入目录 : {input_dir}")
    print(f"输出目录 : {output_dir}")
    print(f"任务数量 : {len(jobs)}")
    print("-" * 60)

    if not input_dir.is_dir():
        print(f"[错误] 输入目录不存在：{input_dir}")
        print("提示：请检查 config.yaml 里的 input_dir，或先放入样例文件。")
        return 1

    if not jobs:
        print("[警告] jobs 列表为空，无事可做。请在 config.yaml 中添加任务。")
        return 0

    total_ok = total_fail = 0

    for idx, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            print(f"\n[{idx}] 无效任务（不是字典），跳过")
            total_fail += 1
            continue

        name = job.get("name", f"job_{idx}")
        jtype = str(job.get("type", "")).lower()
        print(f"\n[{idx}/{len(jobs)}] 任务「{name}」 type={jtype}")

        handler = JOB_HANDLERS.get(jtype)
        if not handler:
            log_fail(f"未知 type「{jtype}」，支持: {', '.join(JOB_HANDLERS)}")
            total_fail += 1
            continue

        ok, fail = handler(job, input_dir, output_dir, dry_run)
        total_ok += ok
        total_fail += fail

    print("\n" + "=" * 60)
    print(f"汇总：成功 {total_ok}  失败 {total_fail}")
    if dry_run:
        print("（以上为预览，未实际写文件）")
    else:
        print(f"输出目录：{output_dir}")
    print("=" * 60)
    return 0 if total_fail == 0 else 2


def main() -> None:
    parser = argparse.ArgumentParser(
        description="T2 固定格式转换/文件批量处理（不调用大模型 API）",
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="配置文件路径（默认 config.yaml）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只预览将要执行的操作，不写入文件",
    )
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_file():
        print(f"[错误] 找不到配置文件：{config_path}")
        print("提示：可先复制 config.example.yaml 为 config.yaml")
        sys.exit(1)
    sys.exit(run(config_path, args.dry_run))


if __name__ == "__main__":
    main()

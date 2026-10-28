# 读书助手（最小演示）

把一本书切成带页码的块，提问时先检索再回答。回答在左边流式出现，右边列出用到的原文；点一条可以展开正文。

当前第一本书是仓库里的美的集团年报 PDF。同一套评测题现分 **18/34**（见 `eval/runs/`）。

## 你需要准备什么

- Python 3.13+（本仓库 `pyproject.toml` 写的是 `>=3.13`）
- 自己的 DeepSeek API 密钥（或兼容 OpenAI 接口的服务）
- 第一本书的 PDF：放到 `data/2025年美的财务报告.pdf`（该路径被 `.gitignore` 忽略，需自备）

## 安装

优先用 **uv**（有的话）：

```powershell
cd finrag_min_hand
uv sync
```

本仓暂无 `uv.lock`；若要用锁文件，可随后执行 `uv lock` 再 `uv sync`。也可用：

```powershell
uv pip install -e .
```

没有 uv 时再用 venv + pip：

```powershell
cd finrag_min_hand
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 密钥（不要提交到 Git）

在项目根目录（本文件夹）新建 `.env`：

```text
DEEPSEEK_API_KEY=你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
FINRAG_MODEL=deepseek-flash
```

可选：

```text
FINRAG_MAX_DISTANCE=12
FINRAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
HF_ENDPOINT=https://hf-mirror.com
```

改过切块 id、换过 embedding 模型、或怀疑索引脏了时，须**重建向量库**：设 `FINRAG_REBUILD_INDEX=1` 后再提问/跑评测，或删掉本目录下的 `chroma_db/`。否则磁盘里可能仍是旧的 `midea_*` id。

`.env` 已在 `.gitignore` 里，不要把真实密钥写进 README 或贴到聊天记录以外的公开地方。

## 打开网页

```powershell
cd finrag_min_hand
.\.venv\Scripts\Activate.ps1
python main.py
```

浏览器打开 <http://127.0.0.1:8000> 。

第一次提问会下载/加载本地嵌入模型，并可能写入 `chroma_db/`，请稍等。

## 命令行演示

```powershell
python cli_demo.py
```

## 跑评测（同一套题）

在 `finrag_min_hand` 目录：

```powershell
python eval/run_baseline.py
```

只跑数字题：

```powershell
python eval/run_baseline.py --types numeric
```

报告会写到 `eval/runs/<时间戳>.jsonl`。进度笔记里对照的分数是 **18/34**。

## 简历怎么说（三句）

1. 做了一个读书问答：先检索书里的段落，再生成回答。  
2. 回答旁能看到命中的页码和原文片段。  
3. 固定 34 道题打分，当前 **18/34**，改检索后可以再跑对比。

## 本阶段故意没做

混合检索、重排序、登录、数据库、公网部署、书架、学习记录、书上划线。那些放到 2026-11-01 演示之后。

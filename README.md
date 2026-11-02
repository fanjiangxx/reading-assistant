# 读书助手（最小演示）

把书（或笔记）切成统一形状的块，提问时先检索再回答。回答在左边流式出现，右边列出用到的原文；点一条可以展开正文。

`data/` 支持 **PDF / TXT / MD** 同一套切块 → 索引 → 提问管线。主语料仍是美的集团年报 PDF；仓库另带 `sample_note.txt` / `sample_note.md` 供多格式验收。财报题集现分 **18/34**（见 `eval/runs/`）。

- PDF：按页切，`page` 为页码。  
- TXT / MD：整文件再切段；没有 PDF 页概念，`page` 固定为 **1**。  
- 往 `data/` 增删文件或改切块规则后，须**重建向量库**（见下），否则索引可能仍是旧块。

## 你需要准备什么

- Python 3.13+（本仓库 `pyproject.toml` 写的是 `>=3.13`）
- 自己的 DeepSeek API 密钥（或兼容 OpenAI 接口的服务）
- 第一本书的 PDF：放到 `data/2025年美的财务报告.pdf`（该路径被 `.gitignore` 忽略，需自备）
- 可选：自备 `.txt` / `.md` 放进 `data/`（与样例一起会被 `load_chunks` 合并入库）

## 安装

优先用 **uv**（有的话）：

```powershell
cd finrag_min_hand
uv sync
```

仓库已带 `uv.lock`。也可用：

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

## 多格式快速自检

重建索引后可用命令行或网页问：

- 「样例笔记的暗号是什么」→ 应提到 **青柠汽水**（来自 `sample_note.txt`）  
- 「样例 Markdown 的口令是什么」→ 应提到 **石桥夜色**（来自 `sample_note.md`）

## 表格题演示（窄范围）

对「家用电器行业 · 原材料」相关问法，`pipeline` 会走抽表/计算，不让模型心算：

- 含「同比」或「增长」→ 用两年金额套公式算同比（金标约 **12.53%**）  
- 含「成本」「金额」或「多少」→ 直接给出表内 2025 年金额（单位：千元）  

命令行单独验收：

```powershell
python table_yoy_demo.py
```

这是演示用的临时规则，不是通用「所有表格自动算」。

## 简历怎么说（三句）

1. 做了一个读书问答：PDF/TXT/MD 同一切块索引管线，先检索再生成。  
2. 回答旁能看到命中原文（PDF 带页码；纯文本 page 记为 1）；部分表格题走程序抽数/计算。  
3. 固定 34 道财报题打分，当前 **18/34**，改检索后可以再跑对比。

## 本阶段故意没做

网页上传按钮、混合检索、重排序、通用表格引擎、登录、数据库、公网部署、书架、学习记录、书上划线。

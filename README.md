# Reading Assistant（读书助手）

面向本地文档的检索增强问答（RAG）演示项目：将 PDF / TXT / Markdown 切块并写入向量库，提问时先检索相关段落再生成回答。Web 端支持流式输出，并在侧栏展示命中原文（含页码）；部分表格类问题走程序抽数与计算，而不是依赖模型心算。

当前示例语料为美的集团年报（PDF 需自备），并附带 TXT / MD 样例。固定评测集基线结果为 **18/34**（见 `eval/runs/`）。

## Features

- 多格式入库：`data/` 下 PDF / TXT / MD 共用同一套切块合同（`id` / `doc_id` / `page` / `text`）
- 向量检索：LangChain + Chroma + 本地 HuggingFace embedding
- Web 演示：FastAPI + SSE（`sources` → `token` → `done`），回答可溯源到原文片段
- 评测脚本：`eval/run_baseline.py`，结果写入 `eval/runs/*.jsonl`
- 表格窄路径：对「原材料」相关的同比 / 金额问法，从 PDF 表格抽取数值后计算或直接回报

## Stack

Python 3.13+ · FastAPI · LangChain · Chroma · PyMuPDF · OpenAI-compatible LLM API（默认 DeepSeek）

## Requirements

- Python `>=3.13`
- LLM API Key（DeepSeek 或兼容 OpenAI Chat Completions 的服务）
- 可选：将年报 PDF 放到 `data/2025年美的财务报告.pdf`（该路径已加入 `.gitignore`）

## Setup

```powershell
git clone https://github.com/fanjiangxx/reading-assistant.git
cd reading-assistant
```

推荐使用 [uv](https://github.com/astral-sh/uv)：

```powershell
uv sync
```

或使用 venv + pip：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Configuration

复制 `env.example` 为 `.env` 并填写密钥（`.env` 不会进入 Git）：

```text
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
FINRAG_MODEL=deepseek-flash
```

常用可选变量：

```text
FINRAG_MAX_DISTANCE=12
FINRAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
HF_ENDPOINT=https://hf-mirror.com
FINRAG_REBUILD_INDEX=1
```

更换切块规则、embedding 模型，或怀疑索引过期时：设置 `FINRAG_REBUILD_INDEX=1` 后重新提问 / 跑评测，或删除项目下的 `chroma_db/` 后重建。

## Usage

### Web

```powershell
python main.py
```

打开 <http://127.0.0.1:8000> 。首次提问会加载本地 embedding 模型并可能写入 `chroma_db/`。

### CLI

```powershell
python cli_demo.py
```

### Evaluation

```powershell
python eval/run_baseline.py
python eval/run_baseline.py --types numeric
```

报告输出到 `eval/runs/<timestamp>.jsonl`。

### Table path smoke test

```powershell
python table_yoy_demo.py
```

对含「原材料」且含「同比 / 增长」或「成本 / 金额 / 多少」的问句，`pipeline` 会走 `table_calc`：同比题用两年金额计算增长率；金额题返回表内 2025 年数值（单位：千元）。该路由为演示范围，不是通用表格引擎。

### Sample documents

`data/sample_note.txt` 与 `data/sample_note.md` 用于验证多格式管线。修改 `data/` 内文件后请重建索引。

## Project layout

| Path | Role |
|------|------|
| `ingest_pdf.py` | PDF / TXT / MD 切块 |
| `store.py` / `vector_store.py` | 切块加载与 Chroma 索引 |
| `retrieve.py` / `generate.py` / `gateway.py` | 检索、生成、LLM 网关 |
| `table_calc.py` | 表格抽取与同比计算 |
| `pipeline.py` | 问答编排（含表格路由） |
| `main.py` / `static/` | Web 入口与前端 |
| `eval/` | 题集、runner、历史跑次 |

## Limitations

当前版本不包含：文档上传 UI、混合检索、重排序、通用表格解析、账号体系、业务数据库、以及生产级部署配置。

## License

暂未指定开源许可证；默认保留所有权利。如需开源分发，可再补充 LICENSE。

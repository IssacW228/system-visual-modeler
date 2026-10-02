# System Visual Modeler / 系统可视化建模

Turn folders, documents, codebases, workflows, architectures, algorithms, and mathematical pipelines into grounded 2D, 2.5D, or 3D interactive models—without reading the whole project into context.

把文件夹、文档、代码库、工作流、架构、算法和数学流水线，快速转化为有证据依据的 2D、2.5D 或 3D 交互模型，同时控制扫描时间和上下文 Token。

[中文](#中文) · [English](#english)

---

## 中文

### 为什么做这个 Skill

大多数可视化工具要么只生成静态流程图，要么为了画面效果牺牲结构准确性。`system-visual-modeler` 把可视化当作一个可检查的解释模型：先扫描证据，再建立组件、端口和关系契约，最后选择真正有意义的维度和交互方式。

它的差异化重点是：

- **轻量且快速**：Lite 会扫描完整目录结构，但只抽取经过权威度、结构差异和问题相关性排序的少量内容；没有固定文件数量上限。
- **按需加深**：提供 Lite、Normal、Deep 三种重量，不必为了快速了解项目而生成完整网页。
- **结构忠实**：每条可见边都应有来源，或明确标记为假设；区分数据、控制、调用、状态、残差和反馈流。
- **维度有语义**：2D、2.5D、3D 由结构需求决定，不把 3D 当作质量标签。
- **可继续提问**：Normal 和 Deep 可生成轻量、MAGMA-inspired 的增量项目记忆。
- **可复用网页交互**：内置 React UI Kit，支持拖拽平移、指针缩放、键盘移动、详情侧栏、Popover、Modal 和移动端底部面板。

### 三种模式

| 模式 | 适合场景 | 默认产物 |
|---|---|---|
| `lite` | 快速了解任意规模项目、文档或文件夹 | 自适应证据索引 + 主要结构的紧凑 2D 总览 |
| `normal` | 交互解释、教学、后续问答 | 类型化模型清单 + 2D/2.5D 模型 + 追踪 + 项目记忆 |
| `deep` | 交付级精度、多模式、复杂状态或明确的 3D 需求 | 完整模型清单 + 有理由的 2D/2.5D/3D + 全面审计 + 项目记忆 |

未指定时，Skill 会选择能够回答问题的最轻模式。

### 工作流程

```text
文件夹 / 文档 / 代码 / 流程
          ↓
完整结构扫描 + 自适应内容取样
          ↓
证据索引：文档、入口、符号、依赖、未知项
          ↓
模型清单：组件、端口、类型、形状、边、模式
          ↓
2D / 2.5D / 3D 表达 + 交互与审计
          ↓
可选增量记忆 → 快速、精准的后续问答
```

### 安装

本仓库同时是 Codex Skill、Claude Code Skill 和 Claude Code 插件（含插件市场清单），任选其一即可。

**Claude Code：插件市场（推荐，可随仓库更新）**

```text
/plugin marketplace add IssacW228/system-visual-modeler
/plugin install system-visual-modeler@system-visual-modeler
```

安装后可以直接描述需求，Claude 会按 Skill 描述自动调用；也可以显式调用：

```text
/system-visual-modeler:system-visual-modeler ./my-project lite 这个项目的主要结构是什么？
```

**Claude Code：个人或项目 Skill**

```bash
git clone https://github.com/IssacW228/system-visual-modeler.git
cp -R system-visual-modeler ~/.claude/skills/system-visual-modeler      # 所有项目可用
# 或：cp -R system-visual-modeler .claude/skills/system-visual-modeler   # 仅当前仓库
```

随后使用 `/system-visual-modeler [路径] [lite|normal|deep] [问题]`。脚本路径通过 `${CLAUDE_SKILL_DIR}` 解析，输出写入当前项目的 `.visual-model/`。

**Codex**

```bash
git clone https://github.com/IssacW228/system-visual-modeler.git
cp -R system-visual-modeler ~/.codex/skills/system-visual-modeler
```

重新打开 Codex 会话，然后使用：

```text
使用 $system-visual-modeler，以 Lite 模式快速解释这个文件夹的主要结构。
```

也可以不指定模式：

```text
使用 $system-visual-modeler，把这个多 Agent 系统做成可交互模型，区分控制流、消息流、工具调用和共享记忆。
```

### 自适应证据扫描

```bash
python3 scripts/scan_evidence.py /path/to/project \
  --mode lite \
  --question "这个项目的主要结构是什么？" \
  --output .visual-model/evidence-index.json
```

扫描器会遍历完整元数据结构（遵守 `.gitignore`，排除依赖、构建产物、缓存以及 `.env`、私钥等敏感文件；`.github/` 等隐藏配置会进入清单），三种模式共用同一份清单，只在内容取样数量上不同；失效的软链接或无法读取的文件会记录在 `unresolved` 中，再按项目级文档、入口文件、结构差异和问题相关性选择内容样本。内容取样数量随规模对数增长，而不是到达固定数量就停止。

### 模型清单验证

```bash
python3 scripts/validate_model.py references/example-manifest.json
```

清单是网页、标签、详情、追踪和模式的统一事实来源。验证器会检查组件、端口、边和引用的一致性。

### 增量项目记忆

Normal 和 Deep 默认可以维护 `.visual-model/memory.json`：

```bash
python3 scripts/project_memory.py build \
  --evidence .visual-model/evidence-index.json \
  --manifest .visual-model/model.json \
  --output .visual-model/memory.json

python3 scripts/project_memory.py update .visual-model/memory.json \
  --evidence .visual-model/evidence-index.json \
  --manifest .visual-model/model.json

python3 scripts/project_memory.py query .visual-model/memory.json \
  "这个组件为什么依赖缓存？" \
  --evidence .visual-model/evidence-index.json
```

更新时会复用未变化的记忆项，仅重新计算受影响的语义关系，并刷新当前的时间、因果和实体图。无变化更新不会重写文件。查询只返回紧凑证据包，不要求 Agent 把完整记忆读进上下文；无匹配时返回 `needs_source_lookup`，避免用无关节点凑答案。

### 可复用 Web UI Kit

`assets/web-model-kit/` 包含无第三方视口依赖的 React 组件：

- `VisualWorkbench`：页头、工具轨、画布、工具面板、详情检查器和组件导航；
- `usePanZoomViewport` / `ViewportSurface`：拖拽、触控、指针中心滚轮缩放、按钮缩放、方向键和平移复位；
- `PopoverCard` / `DialogModal`：短提示和完整帮助弹窗；
- `useExclusiveSurface`：保证主要解释界面互斥；
- 响应式布局：桌面端面板让画布缩窄，移动端使用独立底部区域，不覆盖模型。

组件详情打开后，画布依然可以自由拖拽和缩放。节点默认保持拓扑位置不变，避免交互破坏模型含义。

### 本地基准

以下数据来自 2026-09-14 的本地暖缓存测试，仅反映确定性扫描和记忆脚本，不包含 LLM 生成、浏览器构建或 PDF/Word 等专用解析时间。

| 场景 | 结果 |
|---|---:|
| 85 文件 Lite / Normal / Deep 扫描 | 约 30 / 30 / 40 ms |
| 1,000 文件 Lite 扫描 | 约 50 ms，取样 10 个文件 |
| 10,000 文件 Lite 扫描 | 约 230 ms，取样 14 个文件 |
| 记忆构建 / 无变化更新 / 单项变化更新 / 查询 | 各约 30 ms |
| 85 文件 Lite 紧凑概览 | 估算约 514 Token |
| 10,000 文件 Lite 紧凑概览 | 估算约 607 Token |
| 单次记忆查询证据包 | 估算约 292 Token |

Token 为字符启发式估算，实际数值取决于模型 tokenizer 和项目语言。完整记忆文件保存在本地，正常查询流程不会把它整体加载进上下文。

### 适用范围

适合代码执行、软件架构、Agent 系统、算法、文档结构、数学与张量流水线，以及需要结构化教学解释的网页模型。

不适合纯装饰 3D、普通数据看板，或不要求机制准确的概念插画。

---

## English

### What makes it different

`system-visual-modeler` is designed for fast structural understanding first and polished interactive modeling second.

- **Adaptive intake:** scans the complete file inventory, then samples a logarithmically growing set of authoritative, structurally diverse, question-relevant sources.
- **Three weights:** Lite for orientation, Normal for interactive explanation and memory, Deep for delivery-grade fidelity and audit.
- **Grounded topology:** visible components and edges retain source references; unresolved relationships stay unresolved or are labeled as hypotheses.
- **Meaningful dimensionality:** 2D, 2.5D, and 3D are chosen by what depth actually encodes.
- **Incremental memory:** Normal and Deep can maintain a compact semantic, temporal, causal, and entity graph for follow-up questions.
- **Reusable interaction shell:** the bundled React kit provides non-overlapping panels, drag/pan, pointer-centered zoom, keyboard movement, popovers, modals, and responsive behavior.

### Modes

| Mode | Best for | Default output |
|---|---|---|
| `lite` | Fast orientation at any input scale | Adaptive evidence index + compact 2D overview |
| `normal` | Interactive explanation and follow-up questions | Typed manifest + 2D/2.5D model + trace + project memory |
| `deep` | Delivery-grade fidelity, complex state, or justified 3D | Full manifest + justified dimensionality + complete audit + memory |

When no mode is specified, the skill chooses the lightest mode that can answer the request.

### Install

This repository is a Codex skill, a Claude Code skill, and a Claude Code plugin with its own marketplace manifest. Pick one.

**Claude Code: plugin marketplace (recommended, updatable)**

```text
/plugin marketplace add IssacW228/system-visual-modeler
/plugin install system-visual-modeler@system-visual-modeler
```

Claude invokes the skill automatically from its description, or call it explicitly:

```text
/system-visual-modeler:system-visual-modeler ./my-project lite What is the main structure?
```

**Claude Code: personal or project skill**

```bash
git clone https://github.com/IssacW228/system-visual-modeler.git
cp -R system-visual-modeler ~/.claude/skills/system-visual-modeler      # all projects
# or: cp -R system-visual-modeler .claude/skills/system-visual-modeler  # this repository only
```

Then use `/system-visual-modeler [path] [lite|normal|deep] [question]`. Bundled scripts resolve through `${CLAUDE_SKILL_DIR}`; outputs go to `.visual-model/` in the current project.

**Codex**

```bash
git clone https://github.com/IssacW228/system-visual-modeler.git
cp -R system-visual-modeler ~/.codex/skills/system-visual-modeler
```

Start a new Codex session and invoke `$system-visual-modeler`.

### Quick scan

```bash
python3 scripts/scan_evidence.py /path/to/project \
  --mode lite \
  --question "What is the main structure?" \
  --output .visual-model/evidence-index.json
```

The scanner walks the complete metadata inventory, honors `.gitignore`, and excludes dependency, build, cache, and secret-like files (`.env*`, private keys), while hidden project configuration such as `.github/` stays in the inventory. All modes share that inventory and differ only in how much content they sample; broken symlinks and unreadable files are reported under `unresolved`. It ranks project-level documentation and likely entry points instead of returning the first files encountered or stopping at a fixed count.

### Validate a manifest

```bash
python3 scripts/validate_model.py references/example-manifest.json
```

The manifest is the shared source of truth for components, ports, edges, modes, labels, inspection surfaces, and traces.

### Build, update, and query memory

```bash
python3 scripts/project_memory.py build \
  --evidence .visual-model/evidence-index.json \
  --manifest .visual-model/model.json \
  --output .visual-model/memory.json

python3 scripts/project_memory.py update .visual-model/memory.json \
  --evidence .visual-model/evidence-index.json \
  --manifest .visual-model/model.json

python3 scripts/project_memory.py query .visual-model/memory.json \
  "Why does this component depend on the cache?" \
  --evidence .visual-model/evidence-index.json
```

Unchanged items are reused, semantic edges are recomputed only around changed items, and a no-op update does not rewrite the memory file. Queries return a small evidence bundle rather than loading the whole graph into model context.

### Reusable React kit

Copy or adapt `assets/web-model-kit/` when the host project does not already provide an equivalent shell. It includes:

- a non-overlapping workbench layout;
- drag, touch, wheel zoom, explicit zoom controls, keyboard pan, and reset;
- docked inspectors that keep viewport interaction active;
- contextual popovers and focus-aware modal dialogs;
- component navigation and exclusive explanatory surfaces;
- mobile bottom-panel behavior and reduced-motion support.

### Local benchmark

Warm-cache measurements from 2026-09-14:

| Scenario | Result |
|---|---:|
| 85-file Lite / Normal / Deep scan | ~30 / 30 / 40 ms |
| 1,000-file Lite scan | ~50 ms, 10 content samples |
| 10,000-file Lite scan | ~230 ms, 14 content samples |
| Memory build / no-op update / one-item update / query | ~30 ms each |
| Compact Lite overview, 85 files | ~514 estimated tokens |
| Compact Lite overview, 10,000 files | ~607 estimated tokens |
| One memory query evidence bundle | ~292 estimated tokens |

Token counts are character-based estimates; actual values depend on the model tokenizer and project language. Rich-document extraction and LLM generation are not included.

## Repository structure

```text
system-visual-modeler/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── web-model-kit/
├── references/
│   ├── audit-checklist.md
│   ├── domain-grammars.md
│   ├── example-manifest.json
│   ├── interaction-and-rendering.md
│   ├── model-contract.md
│   ├── modes-and-budgets.md
│   ├── project-memory.md
│   └── web-component-kit.md
├── scripts/
│   ├── project_memory.py
│   ├── scan_evidence.py
│   └── validate_model.py
└── tests/
    └── test_project_memory.py
```

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_model.py references/example-manifest.json
claude plugin validate .
```

The packaging tests keep `SKILL.md`, the Claude plugin manifests, and every bundled path referenced by the skill consistent. The scanner tests cover the shared inventory across modes, lite down-ranking of hidden configuration, `.gitignore` and secret exclusion, broken symlinks, and non-Python language symbols. The project-memory tests cover no-op updates, dependency-aware changes, removal, compact retrieval, and unrelated-query rejection.

## Origin

This skill grew from repeated attempts to model complex systems without allowing attractive visuals to drift away from source truth. The result is a workflow that begins with fast evidence selection, preserves topology and provenance, and scales up to richer interaction only when it adds explanatory value.

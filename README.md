# System Visual Modeler / 系统可视化建模

[中文](#中文) · [English](#english)

`system-visual-modeler` is a reusable Codex skill for turning code execution, software architecture, agent workflows, algorithms, and mathematical or tensor pipelines into accurate, inspectable interactive visual models.

`system-visual-modeler` 是一个可复用的 Codex Skill，用于把代码执行、软件架构、Agent 工作流、算法以及数学/张量流水线，转化为结构准确、可检查、可交互的可视化模型。

---

## 中文

### 它解决什么问题

复杂系统常被画成“看起来很酷”的图，但节点、连线、维度、执行顺序和文字说明并不完全一致。这个 Skill 把可视化视为一个**可执行的解释模型**：先建立系统契约，再设计空间隐喻，最后检查画面、动画、公式与真实机制是否一一对应。

它适合：

- 代码执行过程：调用栈、数据结构、编译流水线、事件循环；
- 软件架构：服务、队列、缓存、数据库、控制流与数据流；
- Agent 架构：规划、工具调用、记忆、路由、并行与回退；
- 算法：搜索、排序、图算法、动态规划、训练与推理流程；
- 数学与张量系统：矩阵运算、维度变化、广播、分支、合并与归一化；
- WebGL / Three.js / React Three Fiber 教学模型。

它不适合仅追求装饰效果的 3D 场景、普通数据看板，或无需结构精度的概念插图。

### 核心原则

1. **语义先于造型**：先确定节点、端口、数据类型、维度和执行顺序，再决定几何体。
2. **连线必须有类型**：数据流、控制流、残差旁路、参数投影、缓存读写不能共用一种含糊的线。
3. **尺寸必须可解释**：宽度、通道数、阵列数量或截面积应与真实维度建立明确比例；必要时使用经过声明的压缩比例。
4. **动画必须服从计算**：粒子不能只是装饰；分叉、并行、汇聚、缓存、逐步执行都应反映真实数据运动。
5. **局部与全局一致**：组件详情页、悬浮标签、公式、张量形状和总览模型必须使用同一份配置。
6. **可验证而非凭感觉**：通过模型清单和审计检查表，发现缺失节点、错误连接、维度不守恒及说明不一致。

### 工作流

```text
需求或源码
   ↓
系统契约：节点 / 端口 / 类型 / 形状 / 不变量
   ↓
视觉语法：几何 / 颜色 / 尺度 / 连接 / 动画
   ↓
交互模型：总览 / 聚焦 / 模式 / 时间轴 / 详情
   ↓
语义审计 + 可读性审计 + 性能审计
```

Skill 中包含：

- `references/model-contract.md`：如何从机制提取可视化系统契约；
- `references/domain-grammars.md`：代码、架构、Agent、算法和张量系统的领域语法；
- `references/interaction-and-rendering.md`：镜头、标签、粒子、模式和渲染策略；
- `references/audit-checklist.md`：语义、视觉、交互、性能和无障碍检查表；
- `references/example-manifest.json`：可机读的示例模型；
- `scripts/validate_model.py`：模型清单验证器。

### 安装

```bash
git clone https://github.com/IssacW228/system-visual-modeler.git
cp -R system-visual-modeler ~/.codex/skills/system-visual-modeler
```

重新打开 Codex 会话后，即可在提示词中调用 `$system-visual-modeler`。

### 使用示例

```text
使用 $system-visual-modeler，把 Decoder-Only Transformer 拆成可交互的 3D 模型。
要求严格表达 Q/K/V 来源、因果注意力、残差旁路、SwiGLU 两分支、张量维度变化，
并提供总览、点击聚焦、训练/推理模式与逐步数据流动画。
```

```text
使用 $system-visual-modeler，把这个多 Agent 客服系统做成可视化网页。
区分控制流、消息流、工具调用和共享记忆，展示并发、超时、重试与人工接管。
```

```text
使用 $system-visual-modeler，可视化这段编译器代码从 AST 到 IR 再到机器码的过程。
每个阶段应能单独查看输入、输出、不变量和错误来源。
```

### 验证模型清单

```bash
python3 scripts/validate_model.py references/example-manifest.json
```

你也可以复制 `example-manifest.json`，把自己的节点、端口、边、张量形状和模式写入同一套结构，再运行验证器检查基础一致性。

### 推荐的交付结构

```text
visual-model/
├── data/               # 唯一事实来源：节点、边、公式、形状、模式
├── scene/              # 3D 场景与领域组件
├── interaction/        # 镜头聚焦、选择、时间轴、模式切换
├── overlays/           # 标签、图例、详情面板与公式
├── validation/         # 语义与几何检查
└── tests/              # 配置、交互与视觉回归测试
```

---

## English

### What it solves

Complex systems are often visualized as attractive diagrams whose nodes, connections, dimensions, execution order, and explanations do not fully agree. This skill treats a visualization as an **executable explanatory model**: establish the system contract first, design a spatial metaphor second, and then audit the scene, animation, formulas, and prose against the real mechanism.

It is useful for:

- code execution: call stacks, data structures, compiler pipelines, and event loops;
- software architecture: services, queues, caches, databases, control flow, and data flow;
- agent systems: planning, tool use, memory, routing, parallelism, and fallback paths;
- algorithms: search, sorting, graph algorithms, dynamic programming, training, and inference;
- mathematical and tensor systems: matrix operations, shape changes, broadcasting, branching, merging, and normalization;
- educational WebGL / Three.js / React Three Fiber experiences.

It is not intended for decorative 3D scenes, ordinary dashboards, or conceptual illustrations where structural fidelity is unimportant.

### Core principles

1. **Semantics before geometry**: define nodes, ports, data types, dimensions, and execution order before choosing shapes.
2. **Every connection is typed**: data flow, control flow, residual bypasses, parameter projections, and cache access must not collapse into one ambiguous line style.
3. **Scale must be explainable**: width, lane count, array count, or cross-section should map to real dimensions, with any visual compression declared explicitly.
4. **Animation follows computation**: particles are not decoration; splits, parallel work, merges, caching, and sequential execution must mirror actual data movement.
5. **Local and global views agree**: component views, floating labels, formulas, tensor shapes, and the overview use the same source of truth.
6. **Validate instead of guessing**: use a model manifest and audit checklist to catch missing nodes, invalid edges, shape violations, and explanation drift.

### Workflow

```text
Requirements or source code
   ↓
System contract: nodes / ports / types / shapes / invariants
   ↓
Visual grammar: geometry / color / scale / connections / motion
   ↓
Interactive model: overview / focus / modes / timeline / details
   ↓
Semantic audit + readability audit + performance audit
```

The skill includes:

- `references/model-contract.md`: extracting a visual system contract from a mechanism;
- `references/domain-grammars.md`: domain grammars for code, architecture, agents, algorithms, and tensor systems;
- `references/interaction-and-rendering.md`: camera, labeling, particles, modes, and rendering guidance;
- `references/audit-checklist.md`: semantic, visual, interaction, performance, and accessibility checks;
- `references/example-manifest.json`: a machine-readable example model;
- `scripts/validate_model.py`: a model-manifest validator.

### Installation

```bash
git clone https://github.com/IssacW228/system-visual-modeler.git
cp -R system-visual-modeler ~/.codex/skills/system-visual-modeler
```

Start a new Codex session, then invoke the skill as `$system-visual-modeler` in your prompt.

### Usage examples

```text
Use $system-visual-modeler to turn a Decoder-Only Transformer into an interactive 3D model.
Accurately represent Q/K/V provenance, causal attention, residual bypasses, the two SwiGLU
branches, and tensor shape changes. Include an overview, click-to-focus inspection,
training/inference modes, and stepwise data-flow animation.
```

```text
Use $system-visual-modeler to visualize this multi-agent support system.
Distinguish control flow, message flow, tool calls, and shared memory. Show concurrency,
timeouts, retries, and human handoff.
```

```text
Use $system-visual-modeler to explain how this compiler moves from AST to IR to machine code.
Each stage should expose its inputs, outputs, invariants, and possible error sources.
```

### Validate a model manifest

```bash
python3 scripts/validate_model.py references/example-manifest.json
```

You can copy `example-manifest.json`, encode your own nodes, ports, edges, tensor shapes, and operating modes, and run the validator to catch basic consistency errors.

### Recommended project layout

```text
visual-model/
├── data/               # Single source of truth: nodes, edges, formulas, shapes, modes
├── scene/              # 3D scene and domain components
├── interaction/        # Camera focus, selection, timeline, mode switching
├── overlays/           # Labels, legends, detail panels, formulas
├── validation/         # Semantic and geometric checks
└── tests/              # Configuration, interaction, and visual regression tests
```

## Repository structure

```text
system-visual-modeler/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── audit-checklist.md
│   ├── domain-grammars.md
│   ├── example-manifest.json
│   ├── interaction-and-rendering.md
│   └── model-contract.md
└── scripts/
    └── validate_model.py
```

## Origin

This skill grew out of an iterative effort to model a Decoder-Only Transformer as a precise 3D factory. That process exposed a general lesson: a useful visualization must preserve structure, dimensionality, provenance, and execution semantics—not merely resemble the subject.

这个 Skill 源于一次对 Decoder-Only Transformer 的精确 3D 工厂建模。反复校正 QKV 来源、注意力对应关系、残差路径、SwiGLU 分支和维度变化后，我们把其中可复用的方法提炼成了这套通用工作流。

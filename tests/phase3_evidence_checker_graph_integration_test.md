测试内容：Evidence Checker 接入 LangGraph 主流程后，会不会自动执行、正确读取 State，并且不破坏原来的 Agent Pipeline

独立组件已经能工作
        ↓
接入主 Graph 后
        ↓
还能不能稳定工作
        ↓
并且不破坏旧功能

Router
↓
Planner
↓
Agent Executor
↓
Search / Extract / Compare
↓
Agent No Tool Call
↓
Finalize
↓
Evidence Checker
↓
END




user:比较 OpenAI 和 Google 在 Agent Tools 设计上的共同点和差异
[Router] task_type=product_comparison, complexity=complex
[Planner]
  1. retrieve_information - 检索 OpenAI 官方文档中关于 Agent Tools（如 Function Calling、Code Interpreter、File Search 等）的设计说明、使用场景和限制
  2. retrieve_information - 检索 Google（如 Gemini 平台）官方文档中关于 Agent Tools（如 Function Calling、Extensions、Code Execution 等）的设计说明、使用场景和限制
  3. extract_information - 从检索到的资料中提取两家公司在工具定义格式、调用机制、上下文管理、错误处理、安全控制等关键设计维度的具体信息
  4. compare_information - 对比 OpenAI 和 Google 在 Agent Tools 设计上的共同点（如支持函数调用、工具结果反馈机制）和差异（如工具生态、多工具并行策略、开发者体验）
  5. validate_information - 交叉验证对比结论，确保信息来自可靠来源且无遗漏关键设计点（如最新版本更新）
  6. generate_report - 生成结构化对比报告，包含共同点、差异、适用场景建议及参考来源

[Agent] Tool Round: 0 -> 1
[Agent] Structured Tool Call:
Tool: company_search
Args: {'company': 'OpenAI', 'query': 'Agent Tools 设计 Function Calling Code Interpreter File Search 使用场景 限制'}
Tool: company_search
Args: {'company': 'Google', 'query': 'Agent Tools 设计 Function Calling Extensions Code Execution 使用场景 限制'}
[Tool Router] tool_rounds=1, MAX_TOOL_ROUNDS=6
Loading vector store from: C:\Users\15637\Desktop\Amily-project\agent-intelligence-platform\data\vector_store
Loading vector store from: C:\Users\15637\Desktop\Amily-project\agent-intelligence-platform\data\vector_store
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 6147.38it/s]
Loading weights: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 391/391 [00:00<00:00, 9748.05it/s]
Vector store loaded successfully.
[Search] company=openai, query=Agent Tools 设计 Function Calling Code Interpreter File Search 使用场景 限制, k=4
Vector store loaded successfully.
[Search] company=google, query=Agent Tools 设计 Function Calling Extensions Code Execution 使用场景 限制, k=4
[Search] retrieved=4
[Search] retrieved=4

[Agent] Tool Round: 1 -> 2
[Agent] Structured Tool Call:
Tool: company_search
Args: {'company': 'OpenAI', 'query': 'Agent Tools 工具定义格式 调用机制 上下文管理 错误处理 安全控制 并行调用'}
Tool: company_search
Args: {'company': 'Google', 'query': 'Agent Tools 工具定义格式 调用机制 上下文管理 错误处理 安全控制 并行调用 MCP A2A'}
[Tool Router] tool_rounds=2, MAX_TOOL_ROUNDS=6
[Search] company=openai, query=Agent Tools 工具定义格式 调用机制 上下文管理 错误处理 安全控制 并行调用, k=4
[Search] company=google, query=Agent Tools 工具定义格式 调用机制 上下文管理 错误处理 安全控制 并行调用 MCP A2A, k=4
[Search] retrieved=4
[Search] retrieved=4

[Agent] Tool Round: 2 -> 3
[Agent] Structured Tool Call:
Tool: extract_company_info
Args: {'company': 'OpenAI', 'topic': 'Agent Tools 设计', 'evidence': 'Evidence 1 (Source: a-practical-guide-to-building-agents.pdf, Page 10): 使用 Agents SDK 定义工具，通过 @function_tool 装饰器定义工具函数，tools=[WebSearchTool(), save_results] 方式配置工具。当工具数量增加时，考虑将任务拆分到多个 agents（见 Orchestration）。\nEvidence 2 (Source: a-practical-guide-to-building-agents.pdf, Page 9): 工具通过底层应用或系统的 API 扩展 agent 能力。对于没有 API 的遗留系统，agent 可以依赖 computer-use 模型通过 web 和应用 UI 直接交互。每个工具应有标准化定义，支持工具与 agent 之间灵活的多对多关系。文档完善、测试充分、可复用的工具提高可发现性、简化版本管理、防止冗余定义。Agent 需要三类工具：Data（检索上下文和信息，如查询数据库、读 PDF、搜索 web）、Action（与系统交... [truncated]'}
Tool: extract_company_info
Args: {'company': 'Google', 'topic': 'Agent Tools 设计', 'evidence': 'Evidence 1 (Source: startup_technical_guide_ai_agents_final.pdf, Page 34): 在 ADK 中，agent 可以使用工具执行超出核心推理模型原生能力的操作。工具是 Python 函数（或 Java 方法），可以实现自包含逻辑或作为更复杂操作的包装器，如调用 API、使用 MCP 访问各种外部系统、或通过 A2A 将任务委托给本地或远程的专门 agent。\nEvidence 2 (Source: startup_technical_guide_ai_agents_final.pdf, Page 52): ADK 将 agent 的工具定义为 Python 函数（或 Java 方法）。这些函数是组件级测试的直接对象。Agent Starter Pack 提供测试基础设施，生成标准 pytest 环境配置在 tests/unit/ 目录。开发者可以立即为 ADK 定义的工具编写单元测试并通过 make test 命令运行。\nEvidence 3 (Source: startup_technical_guide_ai_age... [truncated]'}
[Tool Router] tool_rounds=3, MAX_TOOL_ROUNDS=6
[Tool: extract_company_info] company=OpenAI, topic=Agent Tools 设计
[Tool: extract_company_info] company=Google, topic=Agent Tools 设计

[Agent] Tool Round: 3 -> 4
[Agent] Structured Tool Call:
Tool: compare_companies
Args: {'company_a': 'OpenAI', 'company_a_info': '{"company": "OpenAI", "topic": "Agent Tools 设计", "key_findings": ["工具通过底层应用或系统的 API 扩展 agent 能力。", "对于没有 API 的遗留系统，agent 可以依赖 computer-use 模型通过 web 和应用 UI 直接交互。", "每个工具应有标准化定义，支持工具与 agent 之间灵活的多对多关系。", "文档完善、测试充分、可复用的工具提高可发现性、简化版本管理、防止冗余定义。", "Agent 需要三类工具：Data（检索上下文和信息）、Action（与系统交互执行操作）、Orchestration（agent 本身可作为其他 agent 的工具）。", "建议先最大化单个 agent 的能力，更多 agent 引入额外复杂性和开销，通常单个 agent 带工具就足够。", "复杂工作流中，将 prompts 和 tools 拆分到多个 agents 可提高性能和可扩展性。", "拆分指南包括：复杂逻辑（多个 if-then-else 分支时拆分）、工具过载（问题不仅是工具数量，还有相... [truncated]', 'company_b': 'Google', 'company_b_info': '{"company": "Google", "topic": "Agent Tools 设计", "key_findings": ["工具是定义的能力，使 agent 能做超出核心推理模型原生功能的事情，从执行简单内部计算到通过 API 调用与外部系统交互。", "ADK 中，agent 可以使用工具执行超出核心推理模型原生能力的操作。工具是 Python 函数（或 Java 方法），可以实现自包含逻辑或作为更复杂操作的包装器。", "ADK 围绕丰富的工具生态系统构建，允许 agent 与所有现有工具和数据交互，可连接到生产力工具、工具框架或 agent 框架。", "工具可通过 MCP 共享，创建的 agent 可通过 A2A 共享。", "ADK 提供 RemoteA2aAgent 类，使用 Agent2Agent (A2A) 协议无缝集成分布式系统。"], "technical_details": ["工具是 Python 函数（或 Java 方法），可以实现自包含逻辑或作为更复杂操作的包装器，如调用 API、使用 MCP 访问各种外部系统、或通过 A2A 将任务委托给本地或远... [truncated]', 'topic': 'Agent Tools 设计'}
[Tool Router] tool_rounds=4, MAX_TOOL_ROUNDS=6

[Agent] No Tool Call → Final Answer

[Evidence Checker]
sufficient=False
score=0.62
Evidence Gaps:
  1. 当前已检索的 OpenAI Evidence 未覆盖工具调用机制（如 Function Calling 的具体实现、工具结果反馈机制）的详细说明，无法与 Google 进行完整比较。
  2. 当前已检索的 Google Evidence 未覆盖工具过载处理、多 Agent 拆分的具体指南或性能权衡分析，无法与 OpenAI 的'单 Agent 优先'原则进行对等比较。
  3. 当前已检索的 OpenAI 与 Google Evidence 均未覆盖上下文管理机制（如工具结果如何注入上下文、上下文长度限制）的设计说明。
  4. 当前已检索的 OpenAI 与 Google Evidence 均未覆盖错误处理机制（如工具调用失败的重试策略、错误反馈格式）的设计说明。
  5. 当前已检索的 OpenAI 与 Google Evidence 均未覆盖安全与权限控制机制（如工具访问控制、权限隔离、安全边界）的设计说明。
  6. 当前已检索的 OpenAI 与 Google Evidence 均未提供关于工具数量、Agent 数量对系统性能、延迟或成本影响的量化数据，无法评估两种设计思路在实际运行中的效率差异。
  7. 当前已检索的 OpenAI Evidence 提供了完整的工具分类法（Data/Action/Orchestration），而 Google Evidence 未提供对应的分类体系，导致在'工具如何组织'这一维度上无法直接对比。
Reason: 当前 Evidence 已覆盖工具定义、标准化、外部系统交互、工具复用与共享、工具过载意识等共同点，以及工具分类体系、Agent 协作模式、单 Agent vs 多 Agent 策略、工具生态开放性、开发者控制层级等差异，但存在明显缺口：双方均未覆盖工具调用机制细节（如 Function Calling 的具体实现）、上下文管理、错误处理、安全与权限控制等核心设计维度；Google 侧资料不足，缺乏与 OpenAI 单 Agent 优先原则对等的多 Agent 拆分指南；缺乏性能与成本量化数据；工具分类维度不对等。因此当前 Evidence 只能支持有限结论，不足以全面可靠回答用户问题。

========== RESULT ==========
Task Type: product_comparison
Complexity: complex

Plan:
1. 检索 OpenAI 官方文档中关于 Agent Tools（如 Function Calling、Code Interpreter、File Search 等）的设计说明、使用场景和限制
2. 检索 Google（如 Gemini 平台）官方文档中关于 Agent Tools（如 Function Calling、Extensions、Code Execution 等）的设计说明、使用场景和限制
3. 从检索到的资料中提取两家公司在工具定义格式、调用机制、上下文管理、错误处理、安全控制等关键设计维度的具体信息
4. 对比 OpenAI 和 Google 在 Agent Tools 设计上的共同点（如支持函数调用、工具结果反馈机制）和差异（如工具生态、多工具并行策略、开发者体验）
5. 交叉验证对比结论，确保信息来自可靠来源且无遗漏关键设计点（如最新版本更新）
6. 生成结构化对比报告，包含共同点、差异、适用场景建议及参考来源

Answer:

我已经完成了所有研究阶段。现在进入**第四阶段：生成最终研究报告**。

---

# OpenAI 与 Google 在 Agent Tools 设计上的对比研究报告

## 一、研究概述

本报告基于企业知识库中 OpenAI《A Practical Guide to Building Agents》与 Google《Startup Technical Guide: AI Agents》两份官方技术文档，对两家公司在 **Agent Tools（Agent 工具）** 设计上的共同点与差异进行系统比较。

---

## 二、共同点

### 1. 工具的本质定义一致
两家公司均将工具视为**扩展 Agent 超出核心推理模型原生能力**的关键机制。工具通过函数（或方法）形式定义，可执行从简单内部计算到复杂 API 调用的各类操作。
- **OpenAI**（Page 9）："Tools extend your agent's capabilities by using APIs from underlying applications or systems."
- **Google**（Page 13）："Tools are defined capabilities that enable an agent to do more than the native functions of its core reasoning model."

### 2. 标准化与可测试性
双方均高度重视工具的工程化质量。
- **OpenAI**（Page 9）：强调"每个工具应有标准化定义"、"文档完善、测试充分、可复用的工具提高可发现性、简化版本管理"。
- **Google**（Page 52）：明确工具是 Python 函数（或 Java 方法），是"组件级测试的直接对象"，并提供标准 pytest 测试环境。

### 3. 支持外部系统交互
两者均认可工具作为连接外部世界的桥梁。
- **OpenAI**：通过 API 扩展能力，对无 API 的遗留系统使用 computer-use 模型。
- **Google**：通过 API 调用或包装器实现与外部系统交互。

### 4. 工具复用与共享
- **OpenAI**（Page 9）：强调"可复用的工具提高可发现性、简化版本管理、防止冗余定义"。
- **Google**（Page 30）：通过 MCP 实现工具共享，通过 A2A 实现 Agent 共享。

### 5. 工具过载的应对意识
- **OpenAI**（Page 16）：明确讨论"工具过载"问题——不仅是工具数量，还有相似性或重叠。
- **Google**：虽未直接使用该术语，但其丰富的预构建工具和第三方包装器暗示了通过生态整合管理工具多样性的思路。

---

## 三、关键差异

### 维度一：工具分类体系

| | OpenAI | Google |
|---|---|---|
| **分类方式** | 显式分为三类：**Data**（检索上下文）、**Action**（执行操作）、**Orchestration**（Agent 作为工具） | 未提供显式分类体系，主要从实现方式（函数/方法）和生态连接（MCP/A2A）角度描述 |
| **设计导向** | 分类直接指导工具设计时的功能定位 | 侧重工具如何被定义、测试和互联 |

### 维度二：Agent 间协作模式

| | OpenAI | Google |
|---|---|---|
| **协作方式** | "Agent 作为工具"的层级模式：通过 `agent.as_tool()` 将子 Agent 暴露为 Manager Agent 的工具（Page 19） | 通过 **A2A（Agent2Agent）协议**实现 Agent 间通信，提供 `RemoteA2aAgent` 类集成分布式系统（Page 35） |
| **设计哲学** | 将"智能"本身工具化，实现层级编排 | 强调跨进程、跨系统的开放协议互操作 |

### 维度三：单 Agent vs 多 Agent 策略

| | OpenAI | Google |
|---|---|---|
| **核心原则** | **单 Agent 优先**：建议"先最大化单个 Agent 的能力"，认为更多 Agent 引入额外复杂性和开销（Page 16） | 未提供对等的多 Agent 拆分指南或性能权衡分析 |
| **拆分触发条件** | 复杂逻辑（多 if-then-else 分支）、工具过载（相似性/重叠） | 资料不足，无法对等比较 |

### 维度四：工具生态开放性

| | OpenAI | Google |
|---|---|---|
| **生态策略** | 主要围绕 Agents SDK 自身生态 | 强调**开放协议驱动**：MCP 共享工具、A2A 共享 Agent，支持跨框架（LangChain、LlamaIndex、LangGraph、CrewAI）互操作 |
| **预构建工具** | 提及 WebSearchTool 等 | 明确列出内置工具（Google Search、Code Execution）、Google Cloud 工具集（Vertex AI Search、BigQuery）、第三方包装器（LangchainTool、CrewaiTool） |

### 维度五：开发者控制层级

| | OpenAI | Google |
|---|---|---|
| **控制深度** | 主要通过 SDK 配置工具（`@function_tool` 装饰器、`tools=[...]`） | 提供更底层的自定义路径：继承 `BaseAgent` 并实现 `_run_async_impl` 方法，可完全访问 session 状态并产生事件（Page 34） |
| **调用机制描述** | 未详细展开工具调用链路 | 显式描述完整链路：模型解释工具输出 → 选择工具并格式化请求体（"function-calling"）→ 框架调用工具（Page 30） |

---

## 四、分析判断

> 以下为基于文档事实的分析判断，非文档直接陈述。

1. **设计哲学差异**：OpenAI 的 Agent Tools 设计更偏向"**单 Agent 能力最大化 + 层级编排**"的务实路线，强调在可控复杂度内最大化单 Agent 效能；Google 则更偏向"**开放生态互联**"的平台化路线，通过 MCP/A2A 等开放协议追求跨系统、跨框架的广泛互操作性。

2. **适用场景倾向**：OpenAI 的设计更适合需要精细控制 Agent 内部逻辑、以单 Agent 为核心的中小型工作流；Google 的设计更适合需要整合多种异构系统、跨组织协作的大型企业级场景。

3. **开发者体验差异**：OpenAI 提供了更具体的代码级示例（装饰器、工具配置），上手门槛相对较低；Google 则提供了更丰富的底层控制能力（BaseAgent 继承），适合需要深度定制的开发者，但学习曲线可能更陡。

---

## 五、参考资料与证据局限

### 参考来源
- **OpenAI**：《A Practical Guide to Building Agents》（Pages 9, 10, 16, 19, 22）
- **Google**：《Startup Technical Guide: AI Agents》（Pages 6, 13, 30, 34, 35, 52）

### 证据局限说明
1. **Google 侧资料不足**：Google 研究信息中明确标注"资料不足"，缺乏关于工具过载处理、多 Agent 拆分的具体指南或性能权衡分析，无法与 OpenAI 的"单 Agent 优先"原则进行对等比较。
2. **缺乏性能与成本量化数据**：双方均未提供工具数量、Agent 数量对系统性能/延迟/成本影响的量化数据。
3. **工具分类维度不对等**：OpenAI 提供完整工具分类法，Google 未提供对应分类体系，导致"工具如何组织"维度无法直接对比。
4. **缺少失败模式与安全边界分析**：双方均未讨论工具设计中的失败处理、安全边界、权限控制等关键工程问题。

> ⚠️ 以上局限说明：本次 Evidence 中未发现相关内容，不等于原始文档中不存在，仅代表当前检索范围内资料不足。

============================
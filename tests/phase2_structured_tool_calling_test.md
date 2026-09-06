测试内容：Tool Calling测试
Router
↓
Planner
↓
Structured Tool Calling
↓
company_search



User> OpenAI 的 Agent Tools 是如何设计的？
[Router] task_type=knowledge_query, complexity=simple
[Retrieval] query=OpenAI 的 Agent Tools 是如何设计的？
Loading vector store from: C:\Users\15637\Desktop\Amily-project\agent-intelligence-platform\data\vector_store
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|███████████████████████████████████| 391/391 [00:00<00:00, 7594.68it/s]
Vector store loaded successfully.
[Retrieval] found 8 chunks
  1. startup_technical_guide_ai_agents_final.pdf page=1
  2. startup_technical_guide_ai_agents_final.pdf page=30
  3. startup_technical_guide_ai_agents_final.pdf page=40

========== RESULT ==========
Task Type: knowledge_query
Complexity: simple

Answer:

基于提供的资料，**当前资料不足以支持该结论**。

所提供的全部证据均来自 Google 的《Startup technical guide AI agents》文档，内容围绕 Google 的 Agent Development Kit (ADK)、Agent2Agent (A2A) 协议、Google Agentspace 等产品展开，**没有任何内容涉及 OpenAI 的 Agent Tools 的设计**。

资料中提到的工具设计相关内容（如工具定义与注册、内置工具、第三方互操作性等）均针对 Google ADK 框架，不能用于推断 OpenAI 的产品设计。

============================

User> 比较 OpenAI 和 Google 在 Agent Tools 设计上的共同点和差异。
[Router] task_type=product_comparison, complexity=complex
[Planner]
  1. retrieve_information - 检索 OpenAI 官方文档中关于 Agent Tools（如 Function Calling、Code Interpreter、File Search 等）的设计说明、使用场景和限制
  2. retrieve_information - 检索 Google（如 Gemini API、Vertex AI Agent Builder）官方文档中关于 Agent Tools（如 Function Calling、Extensions、Code Execution 等）的设计说明、使用场景和限制
  3. extract_information - 从检索到的资料中提取关键设计维度：工具定义方式、调用机制、上下文处理、错误处理、安全与权限、扩展性等
  4. compare_information - 基于提取的维度，对比 OpenAI 和 Google 在 Agent Tools 设计上的共同点（如支持函数调用、工具结果反馈机制）和差异（如工具生态、集成方式、模型对工具选择的控制）
  5. validate_information - 交叉验证对比结果，确保信息来自最新官方文档或权威技术博客，并标注来源和日期
  6. generate_report - 生成结构化比较报告，包含共同点、差异、适用场景建议及参考链接，供后续决策使用

[Agent] Structured Tool Call:
Tool: company_search
Args: {'company': 'OpenAI', 'query': 'Agent Tools 设计 Function Calling Code Interpreter File Search 工具定义 调用机制'}
Tool: company_search
Args: {'company': 'Google', 'query': 'Agent Tools 设计 Function Calling Extensions Code Execution 工具定义 调用机制'}
[Search] company=openai, query=Agent Tools 设计 Function Calling Code Interpreter File Search 工具定义 调用机制, k=4
[Search] company=google, query=Agent Tools 设计 Function Calling Extensions Code Execution 工具定义 调用机制, k=4
[Search] retrieved=4
[Search] retrieved=4

[Agent] Structured Tool Call:
Tool: company_search
Args: {'company': 'OpenAI', 'query': 'Function Calling 工具选择 模型控制 上下文 错误处理 安全 Guardrails 权限'}
Tool: company_search
Args: {'company': 'Google', 'query': 'Function Calling 工具选择 模型控制 上下文 错误处理 安全 Guardrails 权限 Vertex AI Gemini'}
[Search] company=openai, query=Function Calling 工具选择 模型控制 上下文 错误处理 安全 Guardrails 权限, k=4
[Search] company=google, query=Function Calling 工具选择 模型控制 上下文 错误处理 安全 Guardrails 权限 Vertex AI Gemini, k=4
[Search] retrieved=4
[Search] retrieved=4

[Agent] Structured Tool Call:
Tool: company_search
Args: {'company': 'OpenAI', 'query': 'Agents SDK 工具生态 扩展性 多Agent编排 工具结果反馈 循环 工具类型'}
Tool: company_search
Args: {'company': 'Google', 'query': 'ADK Agent Development Kit 工具生态 MCP A2A 扩展性 多Agent编排 工具结果反馈'}
[Search] company=openai, query=Agents SDK 工具生态 扩展性 多Agent编排 工具结果反馈 循环 工具类型, k=4
[Search] company=google, query=ADK Agent Development Kit 工具生态 MCP A2A 扩展性 多Agent编排 工具结果反馈, k=4
[Search] retrieved=4
[Search] retrieved=4

[Agent] Structured Tool Call:
Tool: company_search
Args: {'company': 'OpenAI', 'query': '工具结果反馈给模型 循环 模型选择工具 function calling 机制 工具输出返回'}
Tool: company_search
Args: {'company': 'Google', 'query': '模型选择工具 function calling 机制 工具输出返回 循环 工具结果反馈给模型'}
[Search] company=openai, query=工具结果反馈给模型 循环 模型选择工具 function calling 机制 工具输出返回, k=4
[Search] company=google, query=模型选择工具 function calling 机制 工具输出返回 循环 工具结果反馈给模型, k=4
[Search] retrieved=4
[Search] retrieved=4

[Agent] No Tool Call → Final Answer

========== RESULT ==========
Task Type: product_comparison
Complexity: complex

Plan:
1. 检索 OpenAI 官方文档中关于 Agent Tools（如 Function Calling、Code Interpreter、File Search 等）的设计说明、使用场景和限制
2. 检索 Google（如 Gemini API、Vertex AI Agent Builder）官方文档中关于 Agent Tools（如 Function Calling、Extensions、Code Execution 等）的设计说明、使用场景和限制
3. 从检索到的资料中提取关键设计维度：工具定义方式、调用机制、上下文处理、错误处理、安全与权限、扩展性等
4. 基于提取的维度，对比 OpenAI 和 Google 在 Agent Tools 设计上的共同点（如支持函数调用、工具结果反馈机制）和差异（如工具生态、集成方式、模型对工具选择的控制）
5. 交叉验证对比结果，确保信息来自最新官方文档或权威技术博客，并标注来源和日期
6. 生成结构化比较报告，包含共同点、差异、适用场景建议及参考链接，供后续决策使用

Answer:

我已经收集到足够的证据来生成一份结构化的比较报告。让我整理所有信息。

---

# OpenAI 与 Google 在 Agent Tools 设计上的比较报告

## 一、研究背景与方法

本报告基于 OpenAI《A Practical Guide to Building Agents》与 Google《Startup Technical Guide: AI Agents》两份官方技术文档，从工具定义方式、调用机制、上下文处理、错误处理、安全与权限、扩展性等维度对两家公司的 Agent Tools 设计进行对比。

---

## 二、共同点（Commonalities）

### 1. 工具作为 Agent 能力的核心扩展机制
两家公司都认为工具（Tools）是 Agent 超越模型原生能力、与外部系统交互的关键手段。

- **OpenAI**：工具通过底层应用/系统的 API 扩展 Agent 能力；对无 API 的遗留系统，可用 computer-use 模型通过 UI 直接交互（Source: a-practical-guide-to-building-agents.pdf, Page 9）。
- **Google**：工具使 Agent 能执行代码、与外部系统交互、在自身执行上下文之外行动（Source: startup_technical_guide_ai_agents_final.pdf, Page 34）。

### 2. 工具分类逻辑相似（数据类 vs 动作类）
两家公司都将工具划分为"获取信息"与"执行动作"两大类：

- **OpenAI** 将工具分为三类：**Data**（检索上下文/信息）、**Action**（与系统交互执行动作）、**Orchestration**（Agent 作为其他 Agent 的工具）（Page 9）。
- **Google** 强调工具既可以是自包含逻辑，也可以是更复杂操作的包装器（如 API 调用、MCP 访问外部系统、通过 A2A 委派任务给其他 Agent）（Page 34）。

### 3. 模型动态选择工具（Function Calling 机制）
两者都采用"模型根据当前状态动态选择合适工具"的机制：

- **OpenAI**：Agent 利用 LLM 管理工作流执行并做决策，**动态选择合适工具**，始终在明确定义的 guardrails 内运行（Page 4）。
- **Google**：模型分析 prompt 后判断是否需要工具，自动生成并执行查询；采用 **ReAct（Reasoning + Action）** 多轮循环——Reason（推理）→ Act（选择并调用工具）→ Observe（接收工具输出并整合进上下文）（Page 16, 30）。

### 4. 工具结果反馈机制（循环）
两者都支持"工具输出返回给模型，模型据此生成最终响应"的闭环：

- **OpenAI**：模型解释工具输出并生成对用户的响应（Page 30 图示逻辑）。
- **Google**：模型解释工具 B 的输出，生成对用户的响应；工具输出被整合进 Agent 上下文并反馈到下一轮 Reason（Page 16, 30）。

### 5. 工具定义需标准化、可复用
- **OpenAI**：每个工具应有**标准化定义**，支持工具与 Agent 之间灵活的多对多关系；文档完善、经过测试、可复用的工具提升可发现性、简化版本管理（Page 9）。
- **Google**：工具定义需作为**清晰无歧义的 API 契约**，包含函数签名、docstring（语义核心）、返回 schema（Page 35）。

### 6. 支持 Agent 作为工具（多 Agent 编排）
- **OpenAI**：Manager 模式中，中心"manager" Agent 通过工具调用协调多个专门 Agent（Page 17, 19）。
- **Google**：**Agent-as-a-tool** 委派模式，父 Agent 调用专门子 Agent 并保持控制权（Page 35）。

### 7. 强调安全与 Guardrails
- **OpenAI**：将 guardrails 视为分层防御机制，结合 LLM-based、rules-based（regex）、moderation API 等（Page 25）；包含相关性分类器、安全分类器、PII 过滤器、工具安全评估等（Page 26）。
- **Google**：Vertex AI Studio 内置内容过滤，生成式 AI API 提供安全属性评分（Page 63）。

---

## 三、主要差异（Differences）

| 维度 | OpenAI | Google |
|------|--------|--------|
| **核心框架/工具** | **Agents SDK**（Python），通过 `@function_tool` 装饰器、`Agent` 类定义工具 | **ADK（Agent Development Kit）**，工具定义为 Python 函数或 Java 方法 |
| **工具生态与集成** | 相对聚焦于自身 SDK 与内置工具（如 WebSearchTool） | 强调**开放生态**：可连接 Notion、Slack、CRM 等生产力工具，以及 LangChain、LlamaIndex、LangGraph、CrewAI 等第三方框架 |
| **开放标准支持** | 未在资料中强调 MCP/A2A | 深度拥抱 **MCP（Model Context Protocol）** 与 **A2A（Agent2Agent）** 开放标准，用于跨进程/跨系统 Agent 通信 |
| **工具打包方式** | 通过 Agent 的 `tools=[...]` 列表直接挂载 | 引入 **Toolset** 类，将相关工具打包成单一可配置对象（如 BigQueryToolset、MCPToolset） |
| **工具类型细分** | 强调 Data/Action/Orchestration 三类 | 更细粒度：FunctionTool、LongRunningFunctionTool（异步/人机协同）、RemoteA2aAgent（跨进程）、内置工具（Google Search、Code Execution）、Google Cloud toolsets、第三方包装器（LangchainTool、CrewaiTool） |
| **工具定义规范** | 强调标准化定义与可复用性 | 强调工具定义是**模型的 API 契约**：函数签名需 Python 类型提示、docstring 是语义核心、返回需含 status 键（success/error）以区分成败 |
| **编排模式** | Manager（agents as tools）与 Decentralized（handoff）两种模式 | 区分 Agent-as-a-tool（父保持控制）与 sub-agent delegation（完全移交控制权）两种委派模型 |
| **错误处理** | 通过 guardrails 与工具安全评估管理风险 | 通过返回 schema 中的 status 键（success/error）让 Agent 可靠区分成功与失败 |
| **Grounding/检索** | 通过工具（如 WebSearchTool）实现 | 提供多种 grounding 方法：Google Search、Google Maps、RAG 连接自有数据（Page 24） |

---

## 四、关键差异深度解读

### 1. 生态开放性（最显著差异）
**Google 明显更强调开放标准与生态互操作**。ADK 明确支持 MCP（工具共享）和 A2A（Agent 共享），并可直接复用 LangChain、LlamaIndex、LangGraph、CrewAI 等开源生态的工具（Page 30, 35）。而 OpenAI 的资料更聚焦于自身 Agents SDK 的闭环使用。

### 2. 工具定义的技术规范
Google 对工具定义提出了更严格的"API 契约"要求——强制 Python 类型提示、强调 docstring 作为模型语义来源、要求返回字典并含 status 键（Page 35）。OpenAI 则更强调工具的可发现性、版本管理与多对多关系（Page 9）。

### 3. 编排粒度
Google 提供了更细分的工具类型（LongRunningFunctionTool 支持异步与人机协同、RemoteA2aAgent 支持分布式），而 OpenAI 主要围绕 Manager/Decentralized 两种多 Agent 模式展开。

---

## 五、适用场景建议

- **选择 OpenAI**：当团队希望使用统一、聚焦的 Agents SDK 闭环，且主要依赖 OpenAI 模型生态时；其 guardrails 分层防御体系（结合 moderation API）对内容安全要求高的场景较友好。
- **选择 Google（ADK）**：当企业已有大量第三方工具/框架（LangChain、CrewAI 等）或需要跨系统、跨进程的 Agent 协作时；其 MCP/A2A 开放标准支持使其更适合异构、分布式、多云环境，且与 Google Cloud 服务（BigQuery、Vertex AI Search）深度集成。

---

## 六、资料来源与局限说明

**资料来源：**
- OpenAI：《A Practical Guide to Building Agents》（a-practical-guide-to-building-agents.pdf）
- Google：《Startup Technical Guide: AI Agents》（startup_technical_guide_ai_agents_final.pdf）

**局限说明：**
本报告基于知识库中检索到的两份官方技术文档。关于两家公司更细粒度的产品功能（如 OpenAI 的 Code Interpreter/File Search 具体实现、Google Gemini API 的 Function Calling 参数细节、以及各自最新版本 SDK 的更新）在现有资料中覆盖有限。如需更精确的横向对比（如具体 API 参数、定价、模型对工具选择的控制程度差异），建议补充检索两家公司最新的官方 API 文档。

============================
# Phase 3 - Evidence-driven Retry Integration Test

## Test Query

比较 OpenAI 和 Google Agent Tools 在权限控制、错误恢复、
调用延迟、吞吐量和成本方面的具体实现与量化差异。

## Expected

Evidence insufficient
→ Query Rewrite
→ Retry Research
→ Re-evaluation
→ Max 2 retries
→ Graceful termination

## Actual

- Initial Evidence Checker returned insufficient
- Query Rewriter generated targeted company queries
- Retry Research executed successfully
- Message protocol remained valid
- Retry Count progressed to 2
- Evidence Checker re-evaluated the accumulated evidence
- Retry stopped at MAX_RETRY=2
- No unsupported latency/pricing/throughput numbers were invented

## Result

PASS


[Evidence Router]
sufficient=False, retry_count=2, MAX_RETRY=2
[Evidence Router] Retry limit reached (2/2) → END

============================
========== RESULT ==========
============================

Task Type: product_comparison
Complexity: complex

Plan:
1. 检索 OpenAI 官方文档中关于 Agent 工具（如 Assistants API、Function Calling、Agents SDK）的权限控制机制、错误恢复策略、延迟与吞吐量指标、成本定价的原始资料。
2. 检索 Google 官方文档中关于 Agent 工具（如 Vertex AI Agent Builder、Dialogflow CX、Function Calling）的权限控制（IAM、OAuth）、错误恢复机制、延迟与吞吐量指标、成本定价的原始资料。
3. 从检索到的资料中提取两家公司在权限控制（如角色、令牌、作用域）、错误恢复（如重试、回退、超时处理）、调用延迟（如 P50/P95 或典型值）、吞吐量（如 QPS 限制）和成本（如按 token、按请求、按调用）的具体实现与量化数据。
4. 检索第三方基准测试、技术博客或社区评测，获取 OpenAI 与 Google Agent 工具在延迟、吞吐量、成本方面的实测对比数据或经验性量化差异。
5. 将提取的量化数据与实现细节进行结构化对比，识别两者在五个维度上的关键差异、优势与限制，并整理成对比矩阵。
6. 基于对比结果生成最终研究报告，包含具体量化差异、实现机制说明、适用场景建议及数据来源引用。

Answer:

经过第 2 轮补充检索，我获得了关于 Google Agentspace（权限治理）和 Gemini CLI（量化吞吐量参考：60 QPM、1M token context）的新证据。但核心的量化数据（P50/P95 延迟、RPM/TPM、具体定价、重试参数）在两家公司的文档中仍然缺失。

现在我可以综合所有轮次的证据，生成最终研究报告。

---

# OpenAI 与 Google Agent Tools 对比研究报告（最终版）

## 重要声明

本报告综合了**原有 Evidence**、**Evidence-driven Retry 第 1 轮**与**第 2 轮**新增 Evidence。

经过三轮针对性检索，**当前证据库中，两家公司在"调用延迟""吞吐量""成本"三个维度的核心量化数值（P50/P95 延迟、RPM/TPM 限制、按 token/请求的具体定价）仍然缺失**；在"错误恢复"和"权限控制"维度，仅获得定性描述及少量间接量化参考（如 Google Gemini CLI 的 60 QPM）。

本报告将严格区分**文档事实**与**分析判断**，对证据不足的量化维度明确标注"当前 Evidence 不足"，不编造任何性能、价格、功能数据。

---

## 一、权限控制

### OpenAI（文档事实）
来源：a-practical-guide-to-building-agents.pdf

1. **工具风险评级机制**（p26）：为每个工具分配低/中/高风险评级，依据包括只读 vs 写入访问、可逆性、所需账户权限、财务影响。
2. **基于风险评级的自动化动作**（p26）：高风险函数执行前暂停进行 guardrail 检查，或升级到人工处理。
3. **Guardrails 分层防御**（p24-25）：结合 LLM-based guardrails、rules-based guardrails（regex）、OpenAI moderation API。类型包括 relevance classifier、safety classifier、PII filter、moderation。
4. **Guardrails 执行模型**（p31）：默认**乐观执行（optimistic execution）**，guardrails 并发运行，违反约束时触发异常。
5. **Guardrails 实现**（p25）：使用 gpt-4o-mini 作为 hallucination/relevance 分类器和 safety 分类器。

### Google（文档事实）
来源：startup_technical_guide_ai_agents_final.pdf

1. **运行时安全要求**（p18）：管理身份（identity）、网络访问控制、安全通信通道（TLS）。
2. **IAM 角色管理**（p9）：Gemini Cloud Assist 可推荐 IAM 角色、诊断权限错误。
3. **Vertex AI Agent Engine 集成 IAM**（p39）：提供集成身份和访问管理（IAM）。
4. **Google Agentspace 治理**（p45, p8）：单一安全平台，用于治理 agent 对数据和工具的访问权限，尊重所有现有访问控制（access controls）和数据权限（data permissions）。
5. **安全风险缓解**（p56）：Content moderation API、Safety attributes、Recitation checks、Bias evaluation tooling。

### 对比分析（分析判断）

| 维度 | OpenAI | Google |
|------|--------|--------|
| 核心机制 | 工具级风险评级 + Guardrails 分层防御 | 平台级 IAM + Agentspace 治理 + 运行时安全 |
| 控制粒度 | 工具级别（应用层） | 平台/基础设施级（IAM）+ 组织级（Agentspace） |
| 执行方式 | 乐观执行，guardrails 并发运行 | 尊重现有访问控制 + Cloud Trace 可观测 |
| 权限诊断 | 文档未详细展开 | Gemini Cloud Assist 诊断权限错误 |

**分析判断**：OpenAI 侧重**应用层工具治理**（风险评级 + guardrails），Google 提供**三层治理**：基础设施层（IAM/TLS）、平台层（Vertex AI Agent Engine）、组织层（Agentspace 治理 agent 工作力对数据和工具的访问）。Google 在权限治理的层级覆盖上更全面。

**⚠️ 量化指标（权限检查耗时、拒绝率、IAM 角色细粒度）**：当前 Evidence 不足，无法量化对比。

---

## 二、错误恢复

### OpenAI（文档事实）
来源：a-practical-guide-to-building-agents.pdf

1. **人工干预机制**（p31）：两个主要触发条件：
   - **超过失败阈值**：设置 agent 重试或动作限制，超过后升级人工
   - **高风险动作**：敏感、不可逆、高 stakes 动作触发人工监督
2. **Guardrails 异常触发**（p31）：违反约束时抛出异常中断执行。
3. **多 agent handoff**（p23）：通过 handoff 转移控制权，可配置 handoff 回原 agent。

### Google（文档事实）
来源：startup_technical_guide_ai_agents_final.pdf

1. **运行时可靠性要求**（p18）：错误处理、自动重试、全面监控。
2. **组件级测试**（p52）：工具测试有效/无效/边界输入；API 集成处理 success/error/timeout 条件。
3. **可观测性**（p53）：ADK 集成 Google Cloud Trace，instrument 每个 Reason/Act/Observe 步骤。
4. **LongRunningFunctionTool**（p35）：用于异步任务或 human-in-the-loop 工作流。

### 对比分析（分析判断）

| 维度 | OpenAI | Google |
|------|--------|--------|
| 核心机制 | 失败阈值 + 人工升级 | 自动重试 + 错误处理 + 可观测性 |
| 人工介入 | 明确的两类触发条件 | LongRunningFunctionTool 支持 human-in-the-loop |
| 可观测性 | 文档未详细展开 | 深度集成 Cloud Trace + OpenTelemetry（p54） |

**分析判断**：OpenAI 强调**何时升级到人工**（失败阈值/高风险动作），Google 强调**系统自动恢复与可观测性**（自动重试、Cloud Trace）。

**⚠️ 量化参数（重试次数、超时时间、退避策略）**：当前 Evidence 不足，无法量化对比。

---

## 三、调用延迟

### 文档事实

**OpenAI**：
- 模型选择原则（p8）：通过用更小模型替换更大模型来优化延迟。
- **未提供**任何具体延迟数值（P50/P95）或基准。

**Google**：
- Gemini 2.5 Flash-Lite 是最快、最具成本效益的模型，擅长延迟敏感任务（p11）。
- 通过配置 reasoning tokens 可"以可预测的延迟增加换取准确性提升"（p12）。
- **未提供**任何具体延迟数值（P50/P95）或基准。

### 结论

**⚠️ 当前 Evidence 不足，无法对两家公司的调用延迟进行量化对比。** 现有证据仅能确认：
- 两家均提供"用更小/更快模型优化延迟"的策略（OpenAI p8；Google p11）
- Google 提供 reasoning tokens 级别的延迟/准确性权衡控制（p12）

---

## 四、吞吐量

### 文档事实

**OpenAI**：
- **未提供**任何吞吐量数值（QPS、RPM/TPM 限制）。

**Google**：
- Gemini 2.5 Flash-Lite 擅长高吞吐量任务（p11）。
- Vertex AI Agent Engine 提供自动化可扩展性，自动处理不同用户负载（p39）。
- Cloud Run 支持基于资源的自动扩缩（p18）。
- **Gemini CLI 提供量化参考**（p47）：免费访问 Gemini，使用限制为 **1 million token context、60 queries per minute**。
- **未提供**核心 Agent API 的具体吞吐量数值（QPS、RPM/TPM）。

### 结论

**⚠️ 当前 Evidence 不足，无法对两家公司的核心 Agent API 吞吐量进行量化对比。** 

**部分量化参考**：Google 的 Gemini CLI 明确提供 **60 queries per minute** 的速率限制（p47），但这是 CLI 工具而非核心 Agent API 的指标，仅可作为间接参考，不能代表 Vertex AI Agent Engine 或 ADK 的吞吐量上限。

---

## 五、成本

### 文档事实

**OpenAI**：
- 模型选择原则（p8）：通过用更小模型替换更大模型来优化成本。
- **未提供**具体定价数据。

**Google**：
- Gemini 2.5 Flash-Lite 是最具成本效益的模型（p11）。
- Gemini 2.5 Flash 控制质量/成本/速度权衡（p11, p62）。
- Vertex AI Agent Engine 专门优化为成本效益高的自动扩缩方案（p39）。
- Gemini Cloud Assist 提供成本优化建议（FinOps Hub、Cost Optimization dashboard）（p9）。
- 通过配置 reasoning tokens 可"以可预测的成本增加换取准确性提升"（p12）。
- **Gemini CLI 免费访问**（p47）：提供慷慨使用限制（1M token context、60 QPM），Apache 2.0 开源。

### 结论

**⚠️ 当前 Evidence 不足，无法对两家公司的核心 Agent API 成本进行量化对比。** 

**部分量化参考**：Google 的 Gemini CLI 提供**免费访问**（p47），但这是 CLI 工具而非核心 Agent API 的定价，不能代表 Vertex AI 的付费定价结构。

---

## 六、总体对比矩阵

| 维度 | OpenAI | Google | 量化对比 |
|------|--------|--------|----------|
| **权限控制** | 工具级风险评级 + Guardrails 分层防御 + 乐观执行 | 三层治理（IAM + Vertex AI Agent Engine + Agentspace）+ 运行时安全 | ⚠️ 仅定性，无量化数据 |
| **错误恢复** | 失败阈值触发人工升级 + 高风险动作人工监督 | 自动重试 + 错误处理 + Cloud Trace 全程可观测 | ⚠️ 仅定性，无重试次数/超时参数 |
| **调用延迟** | 用更小模型优化延迟（p8） | Flash-Lite 最快 + reasoning tokens 权衡（p11-12） | ❌ 无 P50/P95 数据 |
| **吞吐量** | 无数据 | Vertex AI Agent Engine/Cloud Run 自动扩缩（p18,39）；Gemini CLI 60 QPM（p47） | ❌ 核心 API 无 QPS/RPM/TPM 数据 |
| **成本** | 用更小模型优化成本（p8） | Flash-Lite 最具成本效益 + FinOps 工具 + reasoning tokens 控制（p9,11,12）；Gemini CLI 免费（p47） | ❌ 核心 API 无具体定价数据 |

---

## 七、三轮检索后的关键洞察（分析判断）

### 1. 权限控制：Google 治理层级更全面
Google 通过 **Agentspace**（p45, p8）提供了 OpenAI 现有证据中未明确对应的**组织级 agent 治理**能力——统一治理整个 agent 工作力对数据和工具的访问权限，并尊重现有访问控制。加上 IAM 和 Vertex AI Agent Engine，Google 形成三层治理体系。OpenAI 则聚焦于应用层的工具风险评级与 guardrails。

### 2. 成本/延迟控制：Google 提供更细粒度的控制杠杆
Google 明确提供 **reasoning tokens 级别的控制**（p12），开发者可在"可预测的延迟和成本增加"与"准确性提升"间精确权衡。这是 OpenAI 现有证据中未明确提及的机制。

### 3. 成本管理工具：Google 更丰富
Gemini Cloud Assist 提供 FinOps Hub、Cost Optimization dashboard（p9），而 OpenAI 现有证据仅提及"用更小模型优化成本"这一通用原则。

### 4. 唯一量化参考（间接）
Google 的 Gemini CLI 提供 **60 QPM、1M token context、免费访问**（p47），是当前证据中唯一明确的量化指标，但属于 CLI 工具而非核心 Agent API，仅能作为间接参考。

### 5. 两家策略高度一致
两家均强调"用更小/更快/更便宜模型"作为成本与延迟优化的核心手段（OpenAI p8；Google p11）。

---

## 八、数据来源

| 来源 | 公司 | 引用页码 |
|------|------|----------|
| a-practical-guide-to-building-agents.pdf | OpenAI | p8, p9, p10, p23, p24, p25, p26, p31 |
| startup_technical_guide_ai_agents_final.pdf | Google | p7, p8, p9, p11, p12, p13, p18, p30, p34, p35, p37, p38, p39, p45, p47, p52, p53, p54, p56, p62, p63 |

---

## 九、研究局限与后续建议

**核心局限**：经过三轮检索，当前证据库中**仍缺乏**以下关键量化资料：

1. 两家公司官方 API 文档中的延迟指标（P50/P95）和速率限制（RPM/TPM）
2. 官方定价页面的具体价格数据
3. 错误恢复的具体参数（重试次数、超时时间、退避策略）
4. 权限控制的量化指标（权限检查耗时、拒绝率）
5. 第三方基准测试报告（如 Artificial Analysis、LMSYS 等机构的评测）

**建议后续补充**：
- 检索两家公司官方定价页面与速率限制文档（这些通常不在架构指南中，而在 API 参考文档）
- 检索第三方延迟/吞吐量基准测试报告
- 检索两家公司 API 错误重试策略的官方参数文档

**重要提醒**：当前 Evidence 未覆盖某项能力或数据，**不代表该公司不存在该能力或数据**，仅代表现有资料（架构指南类文档）不足以支撑量化结论。要获得延迟、吞吐量、成本的量化对比，需要获取 API 参考文档、定价页面或第三方实测数据。

----------------------------
Evidence Evaluation
----------------------------

Evidence Sufficient: False
Evidence Score: 0.35

Evidence Gaps:
1. 当前已检索的 OpenAI Evidence 未覆盖调用延迟的具体量化数据（如 P50/P95 延迟、典型响应时间），无法与 Google 进行量化比较。
2. 当前已检索的 Google Evidence 未覆盖调用延迟的具体量化数据（如 P50/P95 延迟、典型响应时间），无法与 OpenAI 进行量化比较。
3. 当前已检索的 OpenAI Evidence 未覆盖吞吐量的具体量化数据（如 QPS、RPM/TPM 限制），无法与 Google 进行量化比较。
4. 当前已检索的 Google Evidence 未覆盖核心 Agent API 吞吐量的具体量化数据（如 QPS、RPM/TPM 限制），仅 Gemini CLI 提供 60 QPM 的间接参考，无法代表 Vertex AI Agent Engine 或 ADK 的吞吐量上限。
5. 当前已检索的 OpenAI Evidence 未覆盖成本的具体量化数据（如按 token、按请求的定价），无法与 Google 进行量化比较。
6. 当前已检索的 Google Evidence 未覆盖核心 Agent API 成本的具体量化数据（如按 token、按请求的定价），仅 Gemini CLI 免费访问作为间接参考，无法代表 Vertex AI 的付费定价结构。
7. 当前已检索的 OpenAI Evidence 未覆盖错误恢复的具体参数（如重试次数、超时时间、退避策略），无法与 Google 进行量化比较。
8. 当前已检索的 Google Evidence 未覆盖错误恢复的具体参数（如重试次数、超时时间、退避策略），无法与 OpenAI 进行量化比较。
9. 当前已检索的 OpenAI Evidence 未覆盖权限控制的量化指标（如权限检查耗时、拒绝率、IAM 角色细粒度），无法与 Google 进行量化比较。
10. 当前已检索的 Google Evidence 未覆盖权限控制的量化指标（如权限检查耗时、拒绝率、IAM 角色细粒度），无法与 OpenAI 进行量化比较。
11. 当前已检索的 Evidence 中缺乏第三方基准测试或社区评测数据，无法提供两家公司在延迟、吞吐量、成本方面的实测对比。

----------------------------
Retry Information
----------------------------

Retry Count: 2

Last Retry Queries:

1.
Company: OpenAI
Query: OpenAI API latency P50 P95 percentile tool calling response time benchmark
Gap: 当前已检索的 OpenAI Evidence 未覆盖调用延迟的具体数值（如 P50/P95）或基准测试数据。

2.
Company: Google
Query: Google Vertex AI Agent Builder Dialogflow CX latency P50 P95 percentile tool calling response time benchmark
Gap: 当前已检索的 Google Evidence 未覆盖调用延迟的具体数值（如 P50/P95）或基准测试数据。

3.
Company: OpenAI
Query: OpenAI API rate limits RPM TPM QPS throughput concurrency limits
Gap: 当前已检索的 OpenAI Evidence 未覆盖吞吐量的具体数值（如 QPS、RPM/TPM 限制）。

4.
Company: Google
Query: Google Vertex AI Agent Builder Dialogflow CX QPS throughput rate limits concurrency
Gap: 当前已检索的 Google Evidence 未覆盖吞吐量的具体数值（如 QPS、RPM/TPM 限制）。

Tool Rounds (current attempt): 3

============================
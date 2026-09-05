# Agent Intelligence Platform

> 基于 LangGraph 的企业 AI 产品研究与决策分析智能体

Agent Intelligence Platform 是一个面向企业 AI 产品研究、知识检索与竞品分析场景的 Research Agent 项目。

当前版本以 OpenAI 与 Google 的公开 AI Agent 技术资料作为知识库数据，基于 **LangGraph + RAG + FAISS + DeepSeek** 构建基础研究流程，实现：

- 企业 AI 文档解析与向量化
- 基于 RAG 的知识检索
- LangGraph 状态管理
- 用户任务分类
- 简单 / 复杂任务路由
- 复杂任务研究计划生成
- 基于检索证据的回答生成

当前版本为项目 MVP 的第一阶段，重点验证：

**Document → RAG → Router → Planner → Retrieval → Answer**

后续将逐步扩展 Structured Tool Calling、Context Engineering、Evidence Check、Retry、Memory 和 Agent Evaluation。

---

## 1. Project Overview

传统企业研究任务通常需要人工完成：

```text
收集资料
↓
阅读文档
↓
整理信息
↓
比较产品
↓
生成研究报告
import json

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.services.llm import get_llm


class RouterResult(BaseModel):
    task_type: str = Field(
        description=(
            "任务类型，只能是 knowledge_query、"
            "competitive_analysis、industry_analysis、"
            "product_comparison、other"
        )
    )

    complexity: str = Field(
        description="任务复杂度，只能是 simple 或 complex"
    )


ROUTER_PROMPT = """
你是企业 AI 研究系统的任务路由器。

你的任务是分析用户问题，并判断：

1. task_type
2. complexity

task_type 可选：

knowledge_query:
单一知识问题，例如询问某个产品或公司的具体能力。

competitive_analysis:
对多个公司或产品进行竞争分析。

industry_analysis:
对一个行业、市场、趋势进行综合研究。

product_comparison:
明确比较多个产品的功能、定位、价格或技术能力。

other:
无法归类的问题。

complexity:

simple:
可以通过一次知识检索和回答完成。

complex:
需要多步骤检索、比较、分析或者生成研究报告。

只返回合法 JSON。

格式：

{{
  "task_type": "knowledge_query",
  "complexity": "simple"
}}

用户问题：

{query}
"""


def router_node(
    state: AgentState,
) -> AgentState:

    llm = get_llm(temperature=0)

    prompt = ChatPromptTemplate.from_template(
        ROUTER_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "query": state["query"],
        }
    )

    content = response.content.strip()

    # 部分模型可能带 markdown code fence
    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    data = json.loads(content)

    result = RouterResult(**data)

    print(
        f"[Router] task_type={result.task_type}, "
        f"complexity={result.complexity}"
    )

    return {
        "task_type": result.task_type,
        "complexity": result.complexity,
    }
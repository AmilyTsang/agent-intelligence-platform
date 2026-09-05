import json

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.services.llm import get_llm


class PlanStep(BaseModel):
    step_id: int

    action: str

    description: str


class ResearchPlan(BaseModel):
    steps: list[PlanStep] = Field(
        description="研究任务执行步骤"
    )


PLANNER_PROMPT = """
你是一个企业 AI 产品研究 Agent 的任务规划器。

请根据用户研究任务生成一个简洁、可执行的研究计划。

当前任务类型：
{task_type}

用户问题：
{query}

要求：

1. 不超过 6 个步骤。
2. 每一步必须是明确的研究动作。
3. 不要直接回答用户问题。
4. 不要虚构已经执行过任何工具。
5. 计划应该服务于后续的信息检索、提取、比较和报告生成。

返回 JSON：

{{
  "steps": [
    {{
      "step_id": 1,
      "action": "retrieve_information",
      "description": "检索公司A的Agent产品资料"
    }}
  ]
}}
"""


def planner_node(
    state: AgentState,
) -> AgentState:

    llm = get_llm(temperature=0)

    prompt = ChatPromptTemplate.from_template(
        PLANNER_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "query": state["query"],
            "task_type": state["task_type"],
        }
    )

    content = response.content.strip()

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    data = json.loads(content)

    plan = ResearchPlan(**data)

    plan_dicts = [
        step.model_dump()
        for step in plan.steps
    ]

    print("[Planner]")

    for step in plan_dicts:
        print(
            f"  {step['step_id']}. "
            f"{step['action']} - "
            f"{step['description']}"
        )

    return {
        "plan": plan_dicts,
    }
from langgraph.prebuilt import ToolNode

from app.tools import tools


tool_node = ToolNode(
    tools
)
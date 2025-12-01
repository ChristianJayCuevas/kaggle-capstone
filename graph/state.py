import operator
from typing import Annotated, List, Dict, Union, Any, Literal
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    plan: List[Dict]           # The steps to execute
    current_step: int          # Index of the current step
    status: str                # 'planning', 'executing', 'paused', 'done'
    last_error: str            # To track HITL needs

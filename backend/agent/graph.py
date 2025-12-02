import operator
from typing import TypedDict, Sequence, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage, SystemMessage
from .tools import ALL_TOOLS # Import the tools defined in tools.py
from config import settings # Assuming GROQ_API_KEY and other settings are here


FORCE_JSON = SystemMessage(content="""\
        When invoking a tool:
        - Return ONLY valid JSON.
        - Do NOT include schema or explanations.
        - Do NOT return "properties", "title", "type", or Pydantic schema.
        - Do NOT include python code.
        - Only return the value for the tool call arguments.
        """)

# --- Configuration ---
MODEL_NAME = "llama-3.1-8b-instant"
# NOTE: Initialize the LLM outside the node function for performance
llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=MODEL_NAME,
    temperature=0.7,
    max_tokens=256,
)
llm_with_tools = llm.bind_tools(ALL_TOOLS)


# -------------------------------------------------------
# State Definition
# -------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    terminate: bool # Flag to signal a forced stop

# -------------------------------------------------------
# Nodes
# -------------------------------------------------------

def llm_node(state: AgentState):
    # print("🔥 llm_node EXECUTED with state:", state)
    messages = [FORCE_JSON] + list(state["messages"])

    result = llm_with_tools.invoke(messages)

    if not getattr(result, "tool_calls", None):
        return {"messages": [result], "end": True}
    
    print(f"9090900000000000000000000000000000:{result}")
    return {"messages": [result]}



def tool_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    tool_results = []

    # Safety check: If no tool calls, return empty
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": tool_results}

    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get("name")
        raw_args = tool_call.get("args")
        tool_id = tool_call.get("id")   # <-- ALWAYS defined here

        # ---------------------------
        # Validate & parse JSON args
        # ---------------------------
        try:
            import json
            if isinstance(raw_args, str):
                tool_args = json.loads(raw_args)
            else:
                tool_args = raw_args
        except Exception:
            tool_results.append(
                ToolMessage(
                    content="Error: Invalid JSON passed to tool. Please return ONLY valid JSON.",
                    tool_call_id=tool_id
                )
            )
            continue

        # ---------------------------
        # Find the tool
        # ---------------------------
        tool = next((t for t in ALL_TOOLS if t.name == tool_name), None)

        if not tool:
            tool_results.append(
                ToolMessage(
                    content=f"Error: Tool '{tool_name}' not found.",
                    tool_call_id=tool_id
                )
            )
            continue

        # ---------------------------
        # Execute tool
        # ---------------------------
        try:
            result = tool.invoke(tool_args)
            tool_results.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                )
            )
        except Exception as e:
            tool_results.append(
                ToolMessage(
                    content=f"Error running tool: {str(e)}",
                    tool_call_id=tool_id
                )
            )

    return {"messages": tool_results}




# -------------------------------------------------------
# Routing Logic (FIXED)
# -------------------------------------------------------
def should_continue(state: AgentState):
    """Router: Decides whether to continue the loop or end the graph."""
    
    # 1. Check the termination flag set by LLM (for final text messages or forced errors)
    if state.get("terminate", False):
        return "end"

    last = state["messages"][-1]

    # 2. Check if LLM produced tool calls
    if getattr(last, "tool_calls", None):
        return "tools"

    # 3. Check for Tool Execution Failures
    if isinstance(last, ToolMessage):
        # We check the content returned by the tool execution.
        if any(err in last.content for err in ["LLM returned invalid JSON", "API ERROR", "CONNECTION ERROR", "Execution Error"]):
            # If a critical error occurred, go to the LLM. The LLM will use its internal instruction 
            # to output an error message and set the terminate flag for the next cycle.
            return "llm_node" 
            
        # If the tool result is clean, continue to the LLM to make the next decision 
        return "llm_node" 

    # 4. Default is to end (Should be a final text message)
    return "end"


# -------------------------------------------------------
# Build Graph
# -------------------------------------------------------
graph = StateGraph(AgentState)

graph.add_node("llm_node", llm_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("llm_node")

graph.add_conditional_edges(
    "llm_node",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    }
)

graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "llm_node": "llm_node", 
        "end": END,
    }
)

# Export the compiled graph
LANGGRAPH_APP = graph.compile()
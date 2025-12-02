import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator, Sequence, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver 
from agent.graph import LANGGRAPH_APP
from database.setup import get_db_session 
from sqlmodel.ext.asyncio.session import AsyncSession
from config import settings
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage

router = APIRouter()

# Use SqliteSaver for prototyping (requires external package)
memory = SqliteSaver.from_conn_string(settings.LANGGRAPH_CHECKPOINTER_URL) 

class ChatInput(BaseModel):
    thread_id: str 
    message: str

# 
async def stream_output(thread_id: str, message: str, session: AsyncSession) -> AsyncGenerator[str, None]:
    """Runs the LangGraph agent and streams results back as SSE."""
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "session": session # Inject the database session for tools
        }
    }
    
    # Convert the input string into the required LangChain HumanMessage object
    input_message = HumanMessage(content=message)
    
    try:
        # Pass the correctly formed message object to astream
        async for chunk in LANGGRAPH_APP.astream({"messages": [input_message]}, config=config, checkpointer=memory):
            
            print(f"Received chunk type: {type(chunk)}, value: {chunk}")
            
            if not isinstance(chunk, dict):
                continue

            # Standard LangGraph chunks contain updates keyed by node name or an internal structure.
            # We look for a change in the 'messages' sequence, which is how LangGraph usually signals output.
            
            # Find the value that contains the updated message list (usually nested under a node name)
            updated_messages = []
            
            # Check for messages in the top-level chunk keys (llm_node or tools)
            for node_key in ['llm_node', 'tools']:
                if node_key in chunk and 'messages' in chunk[node_key]:
                    # LangGraph returns all messages in the node's state, but we only care about the NEW ones.
                    # Simple approach: assume the last message in the list is the one to yield.
                    # A robust approach would compare states, but for streaming, yielding the last is common.
                    if chunk[node_key]['messages']:
                        updated_messages.extend(chunk[node_key]['messages'])

            # Process the updated messages (the newest outputs from the agent/tool)
            for msg in updated_messages:
                
                # 1. Handle regular text content (AIMessage content)
                content = getattr(msg, "content", None)
                if content:
                    yield f"data: {json.dumps({'type': 'TEXT', 'content': content})}\n\n"

                # 2. Handle tool calls requested by the LLM (for execution signal)
                if getattr(msg, "tool_calls", None):
                    yield f"data: {json.dumps({
                        "type": "TOOL_CALL_REQUEST", 
                        "tool_calls": [tc for tc in msg.tool_calls]
                    })}\n\n"
                
                # 3. Handle tool results (ToolMessage content)
                # The content will contain the JSON data or an error string (e.g., "Execution Error")
                if isinstance(msg, ToolMessage) and msg.content:
                    yield f"data: {json.dumps({
                        "type": "TOOL_CALL", # Type for tool result
                        "tool_result": msg.content,
                        "tool_call_id": msg.tool_call_id
                    })}\n\n"

        # Signal end of stream after successful termination
        yield "data: [DONE]\n\n"
            
    except Exception as e:
        # CRITICAL FIX: This catches external errors like Rate Limit
        error_msg = {"type": "ERROR", "content": f"Agent error: {str(e)}"}
        yield f"data: {json.dumps(error_msg)}\n\n"
        
@router.post("/chat/stream")
async def chat_stream(
    input: ChatInput, 
    session: AsyncSession = Depends(get_db_session)
):
    """API endpoint for the conversational interface with streaming response."""
    
    return StreamingResponse(
        stream_output(input.thread_id, input.message, session),
        media_type="text/event-stream"
    )
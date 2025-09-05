# chatbot.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Annotated, Sequence
from loguru import logger
from dotenv import load_dotenv
from llm_tools import LLM_TOOLS
from token_tracking import TokenTracker
import os
import operator
import ast
import sqlite3

load_dotenv()

LOGS_FOLDER = "logs"

# Configuration: Choose between OpenAI and LM Studio
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234")

# LangSmith Configuration
if os.getenv("LANGCHAIN_TRACING_V2").lower() == "true":
    logger.info("LangSmith enabled")
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "campaign-performance-assistant")
    logger.info("LangSmith tracing enabled")
else:
    logger.info("LangSmith disabled")

logger.add(
    f"{LOGS_FOLDER}/chatbot.log", 
    rotation="1 week", 
    retention="4 weeks", 
    level="INFO"
)

# Initialize LLM based on configuration
if USE_LOCAL_LLM:
    logger.info("Using local LLM via LM Studio")
    llm = ChatOpenAI(
        base_url=f"{LM_STUDIO_URL}/v1",
        api_key="not-needed",  # LM Studio doesn't require API key
        temperature=0,
        model="local-model"  # This can be any name since LM Studio ignores it
    )
else:
    logger.info("Using OpenAI")
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo"  # or any other OpenAI model
    )

# LangGraph checkpointer
db_path = "workflow_memory.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)

# Initialize token tracker
token_tracker = TokenTracker(conn)


def message_reducer(existing: Sequence[BaseMessage], new: Sequence[BaseMessage]) -> Sequence[BaseMessage]:
    """Keep only the last n messages to prevent unlimited growth."""

    # Combine existing and new messages
    all_messages = list(existing) + list(new)

    # Keep only the last n messages
    n = 10
    last_n_messages = all_messages[-n:]
    valid_messages = []
    add_all_the_rest = False
    for msg in last_n_messages:
        if isinstance(msg, HumanMessage) or add_all_the_rest: # If it's a human message or we already decided to add all
            add_all_the_rest = True
            valid_messages.append(msg)
    
    return valid_messages


# Define the state for the agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], message_reducer]
    data: dict

def chat_query_with_custom_agent(user_query: str, thread_id: str = "default", user_id: str = None) -> str:
    """Use custom LangGraph agent with SQLite checkpointer."""
    logger.info(f"Processing query with LangGraph agent: {user_query} [Thread: {thread_id}, User: {user_id}]")
    
    # Track tokens - simple counters
    total_input_tokens = 0
    total_output_tokens = 0
    
    try:
        # Use all tools from llm_tools
        all_tools = LLM_TOOLS
        
        # Create a tool lookup dictionary
        tools_dict = {tool.name: tool for tool in all_tools}
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(all_tools)
        
        # Define the agent node with token tracking
        def call_model(state):
            nonlocal total_input_tokens, total_output_tokens
            #logger.info(f"call_model() - User: {user_id}, Thread: {thread_id}")
            messages = state["messages"]
            #logger.info(f"\n\n messages: {messages}")
            data = state.get("data", {})
            logger.info(f"\n\n data: {data}")
            
            response = llm_with_tools.invoke(messages)
            
            # Simple token tracking - extract from response if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                total_input_tokens += usage.get('input_tokens', 0)
                total_output_tokens += usage.get('output_tokens', 0)
                logger.info(f"Tokens - Input: {usage.get('input_tokens', 0)}, Output: {usage.get('output_tokens', 0)}")
            
            return {"messages": [response]}
        
        # Define the tool execution node
        def call_tools(state):
            logger.info(f"call_tools() - Thread: {thread_id}")
            messages = state["messages"]
            data = state.get("data", {})
            last_message = messages[-1]

            # Execute tool calls
            tool_messages = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]
                
                if tool_name in tools_dict:
                    try:
                        response = tools_dict[tool_name].invoke(tool_input)
                        tool_message = ToolMessage(
                            content=str(response),
                            name=tool_name,
                            tool_call_id=tool_call["id"]
                        )
                        tool_messages.append(tool_message)

                        if isinstance(response, dict) and response.get('type') in ['table']:
                            logger.info(f"response: is table")
                            data = response
                            logger.info(f"\n\n data type: {type(data)}")
                            logger.info(f"\n data: {data}")

                        if isinstance(response, dict) and response.get('type') in ['chart']:
                            logger.info(f"response: is chart")
                            data = response
                            logger.info(f"\n\n data type: {type(data)}")
                            logger.info(f"\n data: {data}")

                    except Exception as e:
                        error_message = ToolMessage(
                            content=f"Error executing tool {tool_name}: {str(e)}",
                            name=tool_name,
                            tool_call_id=tool_call["id"]
                        )
                        tool_messages.append(error_message)
                else:
                    error_message = ToolMessage(
                        content=f"Unknown tool: {tool_name}",
                        name=tool_name,
                        tool_call_id=tool_call["id"]
                    )
                    tool_messages.append(error_message)
            
            return {
                "messages": tool_messages,
                "data": data
            }
        
        # Define the condition to decide next step
        def should_continue(state):
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", call_tools)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        # Compile the graph with SQLite checkpointer
        app = workflow.compile(checkpointer=checkpointer)
        
        # Enhanced thread config with user info
        thread_config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id or "anonymous"
            }
        }
        
        logger.info(f"Thread config: {thread_config}")
        
        # Prepare initial messages (only system message and current query)
        # Checkpointer automatically handles conversation history
        initial_messages = [
            SystemMessage(content=(
                "You are a Campaign Performance Assistant that responds polite and professional to queries about campaign data. "
                "Use the available tools to get accurate information, do not make up answers. "
                "If no relevant campaign data is found, respond with: I don't have any information on that."
            )),
            HumanMessage(content=user_query)
        ]
        
        # Run the agent with checkpointer
        logger.info("Before: app.invoke with checkpointer")
        result = app.invoke(
            {"messages": initial_messages, "data": {}}, 
            config=thread_config  # This enables session persistence
        )
        logger.info("After: app.invoke with checkpointer")

        # Save token usage if we tracked any tokens
        if total_input_tokens > 0 or total_output_tokens > 0:
            token_tracker.save_token_usage(
                user_id=user_id or "anonymous",
                thread_id=thread_id,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        # Get the final AI message
        final_message = result["messages"][-1]
        final_message_content = final_message.content
        logger.info(f"Final message content: {final_message_content}")

        if "I don't have any information on that." in final_message_content:
            final_answer = {
                "type": "text",
                "message": final_message_content
            }
            logger.info(f"\n \n final_answer: {final_answer}")

            return final_answer

        data = result["data"]

        # Check if we got a table from tools
        if isinstance(data, dict) and data.get('type') == 'table':
            logger.info(f"final_answer: is table")
            logger.info(f"data type: {type(data)}")
            final_answer = {
                "type": "table",
                "message": "Here are the results",
                "data": data,
            }
            logger.info(f"\n \n final_answer: {final_answer}")
            return final_answer
        
        # Check if we got a chart from tools
        if isinstance(data, dict) and data.get('type') == 'chart':
            logger.info(f"final_answer: is chart")
            logger.info(f"data type: {type(data)}")
            final_answer = {
                "type": "chart",
                "message": "Here are the results",
                "data": data,
            }
            logger.info(f"\n \n final_answer: {final_answer}")
            return final_answer


        # Check if we got meaningful data by examining tool messages
        tool_messages = [msg for msg in result["messages"] if isinstance(msg, ToolMessage)]
        meaningful_data = False
        source_info = None
        
        for tool_msg in tool_messages:
            try:
                tool_content_dict = ast.literal_eval(tool_msg.content)
                if "No relevant campaign documents found" not in tool_msg.content:
                    if "not found" not in tool_msg.content.lower() and "error" not in tool_msg.content.lower():
                        meaningful_data = True
                        source_info = tool_content_dict.get('source')
                        break
            except (ValueError, SyntaxError):
                # If content isn't a valid Python literal, check as string
                if "No relevant campaign documents found" not in tool_msg.content:
                    if "not found" not in tool_msg.content.lower() and "error" not in tool_msg.content.lower():
                        meaningful_data = True
                        break
        
        if not meaningful_data:
            final_message_content = (
                "I couldn't find relevant campaign information for your question. "
                "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
            )
        
        final_answer = {
            "type": "text",
            "message": final_message_content,
            "source": source_info if source_info else ''
        }
        logger.info(f"\n \n final_answer: {final_answer}")

        return final_answer
        
    except Exception as e:
        logger.error(f"Error in custom LangGraph agent: {e}")
        return {
            "type": "text",
            "message": (
            "I couldn't find relevant campaign information for your question. "
            "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
            )
        }


def chat_query(user_query: str, thread_id: str = "default", user_id: str = None) -> str:
    """Main chat function - uses LangGraph agent with SQLite checkpointer."""
    return chat_query_with_custom_agent(user_query, thread_id, user_id)


def clear_memory(thread_id: str = "default", user_id: str = None):
    """Clear conversation history for a specific thread."""
    try:
        # Use the same database connection that the checkpointer uses
        cursor = conn.cursor()
        
        # Clear all checkpoints for this specific thread_id
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        conn.commit()
        
        logger.info(f"Cleared conversation history for thread: {thread_id}, user: {user_id}")
        return {"status": "success", "thread_id": thread_id, "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Error clearing memory for thread {thread_id}, user {user_id}: {e}")
        return {"status": "error", "message": str(e)}


def get_memory_stats(thread_id: str = "default", user_id: str = None):
    """Get statistics about conversation history for a thread."""
    try:
        thread_config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id or "anonymous"
            }
        }
        
        # Get current state for this thread
        checkpoint_tuple = checkpointer.get_tuple(thread_config)
        if checkpoint_tuple and checkpoint_tuple.checkpoint:
            messages = checkpoint_tuple.checkpoint.get("channel_values", {}).get("messages", [])
            return {
                "thread_id": thread_id,
                "user_id": user_id,
                "total_messages": len(messages),
                "user_messages": len([m for m in messages if isinstance(m, HumanMessage)]),
                "ai_messages": len([m for m in messages if isinstance(m, AIMessage)]),
                "storage": "SQLite",
                "status": "active" if messages else "empty"
            }
        else:
            return {
                "thread_id": thread_id,
                "user_id": user_id,
                "total_messages": 0,
                "storage": "SQLite",
                "status": "empty"
            }
            
    except Exception as e:
        logger.error(f"Error getting memory stats for thread {thread_id}, user {user_id}: {e}")
        return {
            "thread_id": thread_id,
            "user_id": user_id,
            "status": "error",
            "message": str(e)
        }

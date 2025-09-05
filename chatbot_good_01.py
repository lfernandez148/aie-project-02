# chatbot.py
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from loguru import logger
from dotenv import load_dotenv
from llm_tools import LLM_TOOLS
import os
import operator
import ast

load_dotenv()

LOGS_FOLDER = "logs"

# Configuration: Choose between OpenAI and LM Studio
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
LM_STUDIO_URL = "http://localhost:1234"

# LangSmith Configuration
if os.getenv("LANGCHAIN_TRACING_V2").lower() == "true":
    logger.info("LangSmith enabled")
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
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

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    max_token_limit=2000  # Limit memory to prevent token overflow
)

logger.info("Memory system initialized with conversation buffer")


# Define the state for the agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    data: dict

def chat_query_with_custom_agent(user_query: str, session_id: str = "default") -> str:
    """Use custom LangGraph agent with manual graph construction."""
    logger.info(f"Processing query with custom LangGraph agent: {user_query}")
    
    try:
        # Get conversation history from memory
        chat_history = memory.chat_memory.messages
        logger.info(f"Retrieved {len(chat_history)} messages from memory")
        
        # Use all tools from llm_tools
        all_tools = LLM_TOOLS
        
        # Create a tool lookup dictionary
        tools_dict = {tool.name: tool for tool in all_tools}
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(all_tools)
        
        # Define the agent node
        def call_model(state):
            logger.info(f"call_model()")
            messages = state["messages"]
            logger.info(f"\n\n messages: {messages}")
            data = state.get("data", {})
            logger.info(f"\n\n data: {data}")
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # Define the tool execution node
        def call_tools(state):
            logger.info(f"call_tools()")
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

                        # Handle special chart/table responses
                        # if isinstance(response, dict) and response.get('type') in ['chart', 'table']:
                        #     logger.info(f"resonse: is chart of table")
                        #     # Save to memory and return immediately
                        #     memory.chat_memory.add_user_message(user_query)
                        #     memory.chat_memory.add_ai_message(response.get('message', ''))
                        #     return response

                        tool_message = ToolMessage(
                            content=str(response),
                            name=tool_name,
                            tool_call_id=tool_call["id"]
                        )
                        tool_messages.append(tool_message)

                        if isinstance(response, dict) and response.get('type') in ['table']:
                            logger.info(f"resonse: is table")
                            data = response #ast.literal_eval(response)
                            logger.info(f"\n\n data type: {type(data)}")
                            logger.info(f"\n data: {data}")

                        if isinstance(response, dict) and response.get('type') in ['chart']:
                            logger.info(f"resonse: is chart")
                            data = response #ast.literal_eval(response)
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
        
        # Compile the graph
        app = workflow.compile()
        
        # Prepare initial state with system message and history
        initial_messages = [
            HumanMessage(content=(
                "You are a Campaign Performance Assistant that responds to queries about campaign data. "
                "Use the available tools to get accurate information, do not make up answers. "
                "If no relevant campaign data is found, respond with: "
                "'I don't have any information on that. "
                "Be polite and professional."
            ))
        ]
        
        # Add conversation history
        initial_messages.extend(chat_history)
        
        # Add current user query
        initial_messages.append(HumanMessage(content=user_query))
        
        # Run the agent
        logger.info(f"Before: app.invoke")
        result = app.invoke({"messages": initial_messages})
        logger.info(f"After: app.invoke")

        # Get the final AI message
        final_message = result["messages"][-1]
        final_answer = final_message.content
        logger.info(f"\n final_answer: {final_answer}")
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
            final_answer = (
                "I couldn't find relevant campaign information for your question. "
                "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
            )
        
        # Save conversation to memory
        memory.chat_memory.add_user_message(user_query)
        memory.chat_memory.add_ai_message(final_answer)
        
        logger.info(f"Saved conversation to memory. Total messages: {len(memory.chat_memory.messages)}")
        
        # Return structured response if we have source info
        if source_info:
            return {
                "type": "text",
                "message": final_answer,
                "source": source_info
            }
        
        return final_answer
        
    except Exception as e:
        logger.error(f"Error in custom LangGraph agent: {e}")
        # Fallback to simple RAG with memory
        return (
            "I couldn't find relevant campaign information for your question. "
            "Please try rephrasing or ask about a specific campaign, metric, topic or segment!"
        )


def call_llm(user_query: str, context: str) -> str:
    """Original LLM call method."""
    logger.info(f"Generating response for query: {user_query}")
    prompt = (
        f"Use only the following campaign data to answer the question.\n"
        f"Campaign Data:\n{context}\n\n"
        f"Question: {user_query}\n"
        f"Answer:"
    )
    response = llm.invoke(prompt)
    logger.success(f"Generated response for query: {user_query}")
    return response.content.strip()


def chat_query(user_query: str) -> str:
    """Main chat function - uses LangGraph agent with tools and memory."""
    return chat_query_with_custom_agent(user_query)


def clear_memory():
    """Clear the conversation memory."""
    memory.clear()
    logger.info("Conversation memory cleared")


def get_memory_stats():
    """Get statistics about the conversation memory."""
    messages = memory.chat_memory.messages
    return {
        "total_messages": len(messages),
        "user_messages": len([m for m in messages if isinstance(m, HumanMessage)]),
        "ai_messages": len([m for m in messages if isinstance(m, AIMessage)]),
        "memory_usage": "active" if messages else "empty"
    }

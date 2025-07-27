# test_lmstudio.py
import requests
import json
from loguru import logger

def test_lmstudio_connection():
    """Test if LM Studio is running and accessible"""
    
    url = "http://localhost:1234/v1/chat/completions"
    
    # Test payload
    payload = {
        "model": "local-model",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Can you respond with 'LM Studio is working!'"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        logger.info("Testing LM Studio connection...")
        logger.info(f"URL: {url}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            logger.success("✅ LM Studio is working!")
            logger.info(f"Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            logger.error(f"❌ LM Studio returned status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to LM Studio")
        logger.error("Make sure LM Studio is running and the API server is enabled")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing LM Studio: {e}")
        return False

def test_langchain_integration():
    """Test LangChain integration with LM Studio"""
    
    try:
        from langchain_openai import ChatOpenAI
        
        logger.info("Testing LangChain integration...")
        
        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="not-needed",
            temperature=0,
            model="local-model"
        )
        
        response = llm.invoke("Say 'LangChain integration is working!'")
        logger.success("✅ LangChain integration is working!")
        logger.info(f"Response: {response.content}")
        return True
        
    except Exception as e:
        logger.error(f"❌ LangChain integration failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== LM Studio Connection Test ===")
    
    # Test 1: Direct API connection
    api_working = test_lmstudio_connection()
    
    if api_working:
        # Test 2: LangChain integration
        langchain_working = test_langchain_integration()
        
        if langchain_working:
            logger.success("🎉 All tests passed! LM Studio is ready to use.")
        else:
            logger.error("❌ LangChain integration failed.")
    else:
        logger.error("❌ LM Studio API test failed.")
        
    logger.info("\n=== Setup Instructions ===")
    logger.info("1. Open LM Studio")
    logger.info("2. Load a model (e.g., Llama, Phi, etc.)")
    logger.info("3. Go to 'Local Server' tab")
    logger.info("4. Click 'Start Server'")
    logger.info("5. Make sure it shows 'Server running on localhost:1234'")
    logger.info("6. Run this test script again") 
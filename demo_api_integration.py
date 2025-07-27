# demo_api_integration.py
"""
Demo script showing how LLM tools now use FastAPI endpoints
instead of direct database queries.
"""

from llm_tools import LLM_TOOLS
import time

def demo_api_integration():
    """Demonstrate the API integration with LLM tools."""
    
    print("🚀 Demo: LLM Tools using FastAPI Endpoints\n")
    print("=" * 50)
    
    # Test each tool
    test_cases = [
        ("get_campaign_summary_stats", {}),
        ("get_campaign_by_id", {"campaign_id": 100}),
        ("get_top_campaigns_by_metric", {"metric": "conversion_rate", "limit": 3}),
        ("get_campaigns_by_topic", {"topic": "Holiday"}),
        ("get_campaigns_by_segment", {"segment": "Premium"}),
        ("compare_campaigns_by_id", {"campaign_id1": 100, "campaign_id2": 101}),
    ]
    
    for tool_name, args in test_cases:
        print(f"\n🔧 Testing: {tool_name}")
        print("-" * 30)
        
        # Find the tool
        tool = None
        for t in LLM_TOOLS:
            if t.name == tool_name:
                tool = t
                break
        
        if tool:
            try:
                start_time = time.time()
                result = tool.invoke(args)
                end_time = time.time()
                
                print(f"✅ Success! (took {end_time - start_time:.2f}s)")
                print(f"📊 Result preview: {result[:200]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Tool '{tool_name}' not found")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n💡 Key Benefits:")
    print("   • LLM tools now call FastAPI endpoints")
    print("   • Better separation of concerns")
    print("   • API can be used independently")
    print("   • Easier to scale and maintain")
    print("   • Consistent data access layer")

if __name__ == "__main__":
    demo_api_integration() 
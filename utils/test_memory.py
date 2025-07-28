#!/usr/bin/env python3
"""
Test script for chatbot memory functionality.
"""

import sys
import os

# Add the parent directory to the path to import chatbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot import chat_query, clear_memory, get_memory_stats


def test_memory_functionality():
    """Test the memory functionality of the chatbot."""
    
    print("🧠 Testing Chatbot Memory Functionality\n")
    print("=" * 50)
    
    # Clear memory to start fresh
    clear_memory()
    print("✅ Memory cleared")
    
    # Test 1: First conversation
    print("\n📝 Test 1: First conversation")
    print("-" * 30)
    
    query1 = "What are the top 3 campaigns by conversion rate?"
    print(f"User: {query1}")
    
    response1 = chat_query(query1)
    print(f"Assistant: {response1[:200]}...")
    
    # Check memory
    stats1 = get_memory_stats()
    print(f"Memory after first query: {stats1['total_messages']} messages")
    
    # Test 2: Follow-up question (should use memory)
    print("\n📝 Test 2: Follow-up question")
    print("-" * 30)
    
    query2 = "Can you compare the first campaign with the second one?"
    print(f"User: {query2}")
    
    response2 = chat_query(query2)
    print(f"Assistant: {response2[:200]}...")
    
    # Check memory
    stats2 = get_memory_stats()
    print(f"Memory after second query: {stats2['total_messages']} messages")
    
    # Test 3: Another follow-up
    print("\n📝 Test 3: Another follow-up")
    print("-" * 30)
    
    query3 = "What was the conversion rate of the first campaign you mentioned?"
    print(f"User: {query3}")
    
    response3 = chat_query(query3)
    print(f"Assistant: {response3[:200]}...")
    
    # Check memory
    stats3 = get_memory_stats()
    print(f"Memory after third query: {stats3['total_messages']} messages")
    
    # Test 4: Clear memory
    print("\n📝 Test 4: Clear memory")
    print("-" * 30)
    
    clear_memory()
    print("✅ Memory cleared")
    
    query4 = "What was the first campaign we discussed?"
    print(f"User: {query4}")
    
    response4 = chat_query(query4)
    print(f"Assistant: {response4[:200]}...")
    
    # Check memory
    stats4 = get_memory_stats()
    print(f"Memory after clearing: {stats4['total_messages']} messages")
    
    print("\n🎉 Memory test completed!")


def test_memory_persistence():
    """Test that memory persists across multiple calls."""
    
    print("\n🧠 Testing Memory Persistence\n")
    print("=" * 50)
    
    # Clear memory
    clear_memory()
    
    # Simulate a conversation
    queries = [
        "Show me campaigns about email marketing",
        "Which one had the highest open rate?",
        "What was the audience size for that campaign?",
        "Can you summarize what we've discussed so far?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"User: {query}")
        
        response = chat_query(query)
        print(f"Assistant: {response[:150]}...")
        
        stats = get_memory_stats()
        print(f"Memory: {stats['total_messages']} messages")
    
    print("\n✅ Memory persistence test completed!")


if __name__ == "__main__":
    test_memory_functionality()
    test_memory_persistence() 
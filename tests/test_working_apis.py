#!/usr/bin/env python3
"""
Working API Test with Correct Model Names
Based on discovered models from api_config.json
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_gemini_working():
    """Test Gemini with working model: gemini-2.5-flash"""
    print("1. Testing Google Gemini API (Primary) - gemini-2.5-flash:")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("   ❌ No API key found")
        return False
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "You are a helpful assistant. Say 'Gemini API working for RAG!' briefly."
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"   ✅ Success: {text.strip()}")
            return True
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_groq_working():
    """Test Groq with working model: llama-3.1-8b-instant"""
    print("\n2. Testing Groq API (Fast) - llama-3.1-8b-instant:")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("   ❌ No API key found")
        return False
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "Say 'Groq API working for RAG!' briefly."}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            text = result['choices'][0]['message']['content']
            print(f"   ✅ Success: {text.strip()}")
            return True
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_groq_premium():
    """Test Groq with premium model: llama-3.3-70b-versatile"""
    print("\n3. Testing Groq API (Premium) - llama-3.3-70b-versatile:")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("   ❌ No API key found")
        return False
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Say 'Groq Premium API working for RAG!' briefly."}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            text = result['choices'][0]['message']['content']
            print(f"   ✅ Success: {text.strip()}")
            return True
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    print("🔑 Testing Working LLM APIs for RAG Implementation")
    print("=" * 60)
    
    working_apis = []
    
    if test_gemini_working():
        working_apis.append("Gemini (gemini-2.5-flash)")
    
    if test_groq_working():
        working_apis.append("Groq Fast (llama-3.1-8b-instant)")
    
    if test_groq_premium():
        working_apis.append("Groq Premium (llama-3.3-70b-versatile)")
    
    print("\n" + "=" * 60)
    print("🎉 Final Results:")
    print(f"Working APIs: {len(working_apis)}")
    for api in working_apis:
        print(f"   ✅ {api}")
    
    if working_apis:
        print(f"\n🚀 Ready for RAG Implementation!")
        print("Recommended setup:")
        print("   Primary: Gemini (good for complex reasoning)")
        print("   Fast: Groq Fast (quick responses)")
        print("   Premium: Groq Premium (best quality)")
        print("\nNext step: Create RAG system architecture!")
    else:
        print("\n❌ No working APIs found")

if __name__ == "__main__":
    main()
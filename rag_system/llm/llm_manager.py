"""
LLM Manager for RAG System
Handles multiple LLM providers with fallback support
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.config import RAGConfig

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages multiple LLM providers with automatic fallback"""
    
    def __init__(self):
        """Initialize LLM manager with available providers"""
        self.providers = self._initialize_providers()
        self.usage_tracking = {}
        self.rate_limits = {
            'gemini': RAGConfig.GEMINI_RATE_LIMIT,
            'groq': RAGConfig.GROQ_RATE_LIMIT
        }
        
        logger.info(f"LLM Manager initialized with providers: {list(self.providers.keys())}")
    
    def _initialize_providers(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available LLM providers"""
        providers = {}
        
        # Gemini provider
        if RAGConfig.GEMINI_API_KEY:
            providers['gemini'] = {
                'api_key': RAGConfig.GEMINI_API_KEY,
                'model': RAGConfig.GEMINI_MODEL,
                'endpoint': 'https://generativelanguage.googleapis.com/v1/models/',
                'active': True
            }
        
        # Groq provider  
        if RAGConfig.GROQ_API_KEY:
            providers['groq'] = {
                'api_key': RAGConfig.GROQ_API_KEY,
                'models': {
                    'fast': RAGConfig.GROQ_FAST_MODEL,
                    'premium': RAGConfig.GROQ_PREMIUM_MODEL
                },
                'endpoint': 'https://api.groq.com/openai/v1/chat/completions',
                'active': True
            }
        
        return providers
    
    def generate_rag_response(self, question: str, context_chunks: List[str], 
                             provider: str = None, model_type: str = 'fast') -> Dict[str, Any]:
        """
        Generate a response using RAG context
        
        Args:
            question: User's question
            context_chunks: Relevant document chunks
            provider: Preferred provider ('gemini', 'groq', or None for auto)
            model_type: For Groq, 'fast' or 'premium'
            
        Returns:
            Dict containing response and metadata
        """
        # Prepare context
        context = self._prepare_context(context_chunks)
        
        # Create RAG prompt
        prompt = self._create_rag_prompt(question, context)
        
        # Determine provider order
        provider_order = self._get_provider_order(provider)
        
        # Try providers in order
        for prov in provider_order:
            if not self._can_make_request(prov):
                logger.warning(f"Rate limit reached for {prov}, trying next provider")
                continue
            
            try:
                if prov == 'gemini':
                    response = self._call_gemini(prompt)
                elif prov == 'groq':
                    model = self.providers['groq']['models'][model_type]
                    response = self._call_groq(prompt, model)
                else:
                    continue
                
                # Track usage
                self._track_usage(prov)
                
                # Format response
                return {
                    'success': True,
                    'response': response,
                    'provider': prov,
                    'model': model if prov == 'groq' else self.providers[prov]['model'],
                    'context_chunks_used': len(context_chunks),
                    'error': None
                }
                
            except Exception as e:
                logger.error(f"Error with provider {prov}: {str(e)}")
                continue
        
        # All providers failed
        return {
            'success': False,
            'response': "Sorry, I'm having trouble generating a response right now. Please try again later.",
            'provider': None,
            'model': None,
            'context_chunks_used': len(context_chunks),
            'error': "All LLM providers failed"
        }
    
    def _prepare_context(self, chunks: List[str], max_length: int = None) -> str:
        """Prepare context from chunks, respecting length limits"""
        max_length = max_length or RAGConfig.MAX_CONTEXT_LENGTH
        
        if not chunks:
            return "No relevant context found."
        
        # Combine chunks with separators
        context_parts = []
        current_length = 0
        
        for i, chunk in enumerate(chunks):
            chunk_text = f"Context {i+1}:\n{chunk}\n"
            if current_length + len(chunk_text) > max_length:
                break
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, question: str, context: str) -> str:
        """Create a well-structured RAG prompt"""
        prompt = f"""You are a helpful assistant that answers questions based on the provided context from program documentation.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based ONLY on the information provided in the context above
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Include specific details and examples from the context when relevant
4. If you reference specific information, mention which context section it came from
5. Keep your response clear, concise, and helpful
6. If the question is not related to the program documentation, politely redirect the user

ANSWER:"""
        
        return prompt
    
    def _get_provider_order(self, preferred: str = None) -> List[str]:
        """Get provider order with preferred provider first"""
        available = [p for p in self.providers.keys() if self.providers[p]['active']]
        
        if preferred and preferred in available:
            # Put preferred first, others follow
            order = [preferred] + [p for p in available if p != preferred]
        else:
            # Use default order (Gemini first for quality, Groq for speed)
            order = []
            if 'gemini' in available:
                order.append('gemini')
            if 'groq' in available:
                order.append('groq')
        
        return order
    
    def _can_make_request(self, provider: str) -> bool:
        """Check if we can make a request to this provider (rate limiting)"""
        if provider not in self.usage_tracking:
            self.usage_tracking[provider] = {
                'requests_today': 0,
                'requests_this_minute': 0,
                'last_request_time': None,
                'last_minute_reset': datetime.now()
            }
        
        now = datetime.now()
        usage = self.usage_tracking[provider]
        limits = self.rate_limits.get(provider, {})
        
        # Reset minute counter if needed
        if now - usage['last_minute_reset'] >= timedelta(minutes=1):
            usage['requests_this_minute'] = 0
            usage['last_minute_reset'] = now
        
        # Reset daily counter if needed (simple daily reset at midnight)
        if usage['last_request_time']:
            last_date = usage['last_request_time'].date()
            if now.date() > last_date:
                usage['requests_today'] = 0
        
        # Check limits
        per_minute_limit = limits.get('requests_per_minute', float('inf'))
        per_day_limit = limits.get('requests_per_day', float('inf'))
        
        return (usage['requests_this_minute'] < per_minute_limit and 
                usage['requests_today'] < per_day_limit)
    
    def _track_usage(self, provider: str):
        """Track API usage for rate limiting"""
        if provider not in self.usage_tracking:
            self.usage_tracking[provider] = {
                'requests_today': 0,
                'requests_this_minute': 0,
                'last_request_time': None,
                'last_minute_reset': datetime.now()
            }
        
        usage = self.usage_tracking[provider]
        usage['requests_today'] += 1
        usage['requests_this_minute'] += 1
        usage['last_request_time'] = datetime.now()
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        url = f"{self.providers['gemini']['endpoint']}{self.providers['gemini']['model']}:generateContent"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }],
            'generationConfig': {
                'temperature': RAGConfig.TEMPERATURE,
                'maxOutputTokens': RAGConfig.MAX_TOKENS
            }
        }
        
        # Add API key to URL
        url += f"?key={self.providers['gemini']['api_key']}"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception(f"Unexpected Gemini response format: {result}")
        else:
            raise Exception(f"Gemini API error {response.status_code}: {response.text}")
    
    def _call_groq(self, prompt: str, model: str) -> str:
        """Call Groq API"""
        headers = {
            'Authorization': f"Bearer {self.providers['groq']['api_key']}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': RAGConfig.TEMPERATURE,
            'max_tokens': RAGConfig.MAX_TOKENS
        }
        
        response = requests.post(
            self.providers['groq']['endpoint'],
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"Unexpected Groq response format: {result}")
        else:
            raise Exception(f"Groq API error {response.status_code}: {response.text}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        stats = {
            'providers': {},
            'available_providers': list(self.providers.keys()),
            'active_providers': [p for p in self.providers.keys() if self.providers[p]['active']]
        }
        
        for provider, usage in self.usage_tracking.items():
            limits = self.rate_limits.get(provider, {})
            stats['providers'][provider] = {
                'requests_today': usage['requests_today'],
                'requests_this_minute': usage['requests_this_minute'],
                'daily_limit': limits.get('requests_per_day', 'unlimited'),
                'minute_limit': limits.get('requests_per_minute', 'unlimited'),
                'can_make_request': self._can_make_request(provider),
                'last_request': usage['last_request_time'].isoformat() if usage['last_request_time'] else None
            }
        
        return stats
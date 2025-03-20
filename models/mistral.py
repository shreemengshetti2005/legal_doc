import requests
import yaml
import logging
import time
import os
from utils.load_config import load_config

# Setup logging
logger = logging.getLogger(__name__)

# Load config
config = load_config()
if config:
    API_KEY = config['llm']['mistral_api_key']
    BASE_URL = config['llm']['mistral_base_url']
    MAX_TOKENS = config['llm']['max_tokens']
else:
    logger.error("Failed to load configuration")
    API_KEY = ""
    BASE_URL = "https://api.mistral.ai/v1"
    MAX_TOKENS = 4096

# Cache directory
CACHE_DIR = os.path.join("cache", "mistral")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(text):
    """Generate a unique cache file path based on input text"""
    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash[:10]}.txt")

def mistral_summarize(text, use_cache=True, retries=3, delay=2):
    """
    Summarizes the provided legal document text using Mistral API.
    Includes caching and retry logic.
    """
    # Check cache first if enabled
    cache_path = get_cache_path(text)
    if use_cache and os.path.exists(cache_path):
        logger.info("Using cached Mistral summary")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Prepare prompt for better legal summary
    system_prompt = """You are a legal document analysis assistant. Analyze the provided document and create a comprehensive summary that includes:
1. Key contract terms and obligations
2. Important deadlines and dates
3. Potential legal risks or ambiguities
4. Rights and responsibilities of each party
5. Termination conditions
6. Jurisdiction Handling: Recognize and interpret jurisdiction-specific legal terminology.
Your summary should be detailed yet concise, focusing on legally significant elements."""

    user_prompt = f"Please summarize the following legal document:\n\n{text}"
    
    # If text is too long, truncate it
    if len(user_prompt) > 24000:  # Mistral context limit
        logger.warning("Document too long, truncating for API")
        user_prompt = user_prompt[:24000] + "\n[Document truncated due to length]"
    
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.3  # Lower temperature for more focused summary
    }
    
    # Retry logic
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json().get("choices")[0].get("message").get("content")
                
                # Cache the result
                if use_cache:
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        f.write(result)
                        
                return result
            elif response.status_code == 429:  # Rate limit
                wait_time = int(response.headers.get('Retry-After', delay * (attempt + 1)))
                logger.warning(f"Rate limited by Mistral API. Waiting {wait_time} seconds.")
                time.sleep(wait_time)
            else:
                logger.error(f"Mistral API error: {response.status_code}, {response.text}")
                time.sleep(delay * (attempt + 1))
        except Exception as e:
            logger.error(f"Request to Mistral API failed: {e}")
            time.sleep(delay * (attempt + 1))
    
    # If all retries failed
    logger.error("All attempts to reach Mistral API failed")
    return "Error: Unable to generate summary. Please check API connectivity and try again."

def mistral_analyze_clauses(clauses, use_cache=True):
    """
    Analyze individual clauses to identify risks and obligations.
    """
    results = []
    
    # Join clauses for single API call (more efficient)
    formatted_clauses = "\n\n".join([f"Clause {i+1}: {clause}" for i, clause in enumerate(clauses)])
    
    system_prompt = """You are a legal expert analyzing contract clauses. For each clause:
1. Identify the type of clause (e.g., indemnification, termination, confidentiality)
2. Rate the risk level (Low, Medium, High)
3. Explain potential issues or concerns
4. Suggest improvements if applicable"""

    user_prompt = f"Please analyze these contract clauses:\n\n{formatted_clauses}"
    
    # Use the same API call structure as summarize but with different prompts
    try:
        url = f"{BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": 0.2
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        
        if response.status_code == 200:
            return response.json().get("choices")[0].get("message").get("content")
        else:
            logger.error(f"Error analyzing clauses: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to analyze clauses: {e}")
        return None
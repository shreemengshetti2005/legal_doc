import requests
import yaml

# Load config
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

API_KEY = config['llm']['deepseek_api_key']
BASE_URL = config['llm']['deepseek_base_url']  # Use base URL from config
MAX_TOKENS = config['llm']['max_tokens']

def deepseek_extract(text):
    """
    Extracts legal insights using DeepSeek API.
    """
    url = f"{BASE_URL}/chat/completions"  # Updated URL usage

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f"Extract insights from: {text}"}],
        "max_tokens": MAX_TOKENS
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("choices")[0].get("message").get("content")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

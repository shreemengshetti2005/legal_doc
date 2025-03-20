import yaml
import os

def load_config():
    """
    Load the YAML configuration file and return the config dictionary.
    """
    # Get the base directory (the root of your project)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Path to the YAML config file
    config_path = os.path.join(BASE_DIR, "config", "config.yaml")

    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


# ✅ Example usage:
if __name__ == "__main__":
    config = load_config()

    if config:
        # Accessing LLM keys
        mistral_api_key = config["llm"]["mistral_api_key"]
        deepseek_api_key = config["llm"]["deepseek_api_key"]

        # Accessing Neo4j credentials
        neo4j_uri = config["neo4j"]["uri"]
        neo4j_user = config["neo4j"]["user"]
        neo4j_password = config["neo4j"]["password"]

        print("Mistral API Key:", mistral_api_key)
        print("DeepSeek API Key:", deepseek_api_key)
        print("Neo4j URI:", neo4j_uri)
        print("Neo4j User:", neo4j_user)

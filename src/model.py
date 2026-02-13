import requests
import json
import logging
from typing import Optional

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLCoderAgent:
    def __init__(self, model_name: str = "sqlcoder"):
        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"
        logger.info(f"Ollama SQLCoderAgent initialized for model: {self.model_name}")

    def generate_response(self, prompt: Optional[str]):
        if not prompt:
            return {"raw": "", "processed": "Error: Prompt is empty. Please provide a valid prompt."}

        logger.info(f"Sending request to Ollama for model {self.model_name}...")
        logger.info(f"Prompt ends with: ...{prompt[-100:]}")

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 600
            }
        }

        try:
            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            raw_text = result.get("response", "").strip()

            # debug response metadata
            logger.info(f"Response done: {result.get('done', False)}")
            logger.info(f"Response length: {len(raw_text)} characters")
            logger.info(f"Raw response from Ollama: {raw_text}")


            text = raw_text

            if not text:
                logger.warning("Empty response from Ollama. Model may not be loaded or prompt format issue.")
                return {"raw": raw_text, "processed": ""}

            text = text.replace("<s>", "").replace("</s>", "").replace("[SQL]", "")

            for delimiter in ["[QUESTION]", "[/QUESTION]", "###", "[/SQL]"]:
                if delimiter in text:
                    text = text.split(delimiter)[0]

            text = text.strip()

            import re
            text = re.sub(r';(\s*\n){2,}.*$', ';', text, flags=re.DOTALL)

            table_names = [
                "User", "TaskType", "Metric", "Competition", "CompetitionConfig",
                "Prize", "Participation", "Dataset", "FileArtifact", "Submission",
                "Evaluation", "LeaderboardRow", "CodeKernel"
            ]
            for table_name in table_names:
                text = re.sub(rf'\b{table_name}\b(?!")', f'"{table_name}"', text)

            text = ' '.join(text.split())
            text = text.strip()

            logger.info(f"Generated SQL: {text}")
            return {"raw": raw_text, "processed": text}

        except Exception as e:
            logger.error(f"Error connecting to Ollama: {e}")
            return {"raw": "", "processed": f"Error: {e}. Make sure Ollama is running and model '{self.model_name}' is pulled."}

if "__main__" == __name__:
    agent = SQLCoderAgent()
    response = agent.generate_response("SELECT * FROM users")
    print(response)

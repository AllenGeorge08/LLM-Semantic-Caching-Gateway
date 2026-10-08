from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from app.config.config import OPENAI_GPT_LUNA_PRO, OPENAI_OSS_120B
import os
from dotenv import load_dotenv
import time

load_dotenv(override=True)

try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
except:
    print("Groq API Key not found. Groq based Models won't work")

try:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
except:
    print("OpenRouter API Key not found. Groq based Models won't work")


# ollama run deepseek-r1
deepseek_model = ChatOpenRouter(
    model="deepseek/deepseek-v4.1-flash",
    max_tokens=1000,
    api_key=OPENROUTER_API_KEY,
    max_retries=3,
    timeout=60_000,
)

openai_120b = ChatGroq(model=OPENAI_OSS_120B, max_retries=3)


claude_haiku = ChatOpenRouter(
    model="anthropic/claude-haiku-4.5",
    max_tokens=256,
    api_key=OPENROUTER_API_KEY,
    max_retries=2,
    timeout=60_000,
)

gpt_luna = ChatOpenRouter(
    model="openai/gpt-6-luna-pro",
    max_tokens=1000,
    api_key=OPENROUTER_API_KEY,
    max_retries=3,
    timeout=60_000,
)

gemini_flash = ChatOpenRouter(
    model="google/gemini-2.5-flash-lite",
    max_tokens=1500,
    api_key=OPENROUTER_API_KEY,
    max_retries=3,
    timeout=60_000,
)


MODEL_REGISTRY = {
    "deepseek-flash-v4": deepseek_model,
    "gpt-oss-120b": openai_120b,
    "gemini_2.5_flash": gemini_flash,
    "claude_haiku_4.5": claude_haiku,
    "gpt_luna_pro": OPENAI_GPT_LUNA_PRO,
}

available_models = list(MODEL_REGISTRY.keys())  # names only, JSON-safe


def get_llm_response(prompt):
    response = deepseek_model.invoke(prompt)
    return response.content


class Router:
    def invoke(self, model: str, prompt: str, retries: int = 2):
        for attempt in range(retries + 1):
            try:
                if model == "deepseek-flash-v4":
                    response = deepseek_model.invoke(prompt)
                    return response.content
                elif model == "gpt-oss-120b":
                    response = openai_120b.invoke(prompt)
                    return response.content
                elif model == "gemini_2.5_flash":
                    response = gemini_flash.invoke(prompt)
                    return response.content
                elif model == "claude_haiku_4.5":
                    response = claude_haiku.invoke(prompt)
                    return response.content
                else:
                    response = gpt_luna.invoke(prompt)
                    return response.content
            except Exception as e:
                if attempt == retries:
                    raise

                time.sleep(1)

    def supported_models(self):
        return available_models

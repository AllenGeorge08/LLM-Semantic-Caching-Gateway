from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from app.config.config import DEEPSEEK_OLLAMA_MODEL,OPENAI_OSS_120B,QWEN_OLLAMA_MODEL
import os 
from dotenv import load_dotenv

load_dotenv()

try:
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
except:
    print("Groq API Key not found. Groq based Models won't work")



# ollama run deepseek-r1 
deepseek_model = ChatOllama(
    model=DEEPSEEK_OLLAMA_MODEL,
    validate_model_on_init=True,
    temperature=0.8 
)

qwen_model = ChatOllama(
    model=QWEN_OLLAMA_MODEL,
    validate_model_on_init=True,
    temperature=0.8 
)

openai_120b = ChatGroq(
    model="openai/gpt-oss-20b",
    max_retries=3
)

MODEL_REGISTRY = {
    "deepseek-r1": deepseek_model,
    "qwen_3.8": qwen_model,
    "gpt-oss-120b": openai_120b,
}
available_models = list(MODEL_REGISTRY.keys())  # names only, JSON-safe

def get_llm_response(prompt):
    response = deepseek_model.invoke(prompt)
    return response.content 


class Router:
    def invoke(self,model: str,prompt: str):
        if model=="deepseek-r1":
             response = deepseek_model.invoke(prompt)
             return response.content 
        elif model=="qwen_3.8":
            response = qwen_model.invoke(prompt)
            return response.content 
        else:
            if not GROQ_API_KEY:
                
                raise ValueError("Configure your groq api key to use this model")
            else:
                messages = [
                ("system","You're an reasoning model. Provide concise,to the point and high quality answers"),
                ("human",prompt)
            ]
                response = openai_120b.invoke(messages)
                return response.content
    
    def supported_models(self):
        return available_models



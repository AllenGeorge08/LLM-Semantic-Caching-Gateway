from langchain_ollama import ChatOllama
from app.config.config import LLM_MODEL

# ollama run deepseek-r1 
model = ChatOllama(
    model=LLM_MODEL,
    validate_model_on_init=True,
    temperature=0.8 
)

def get_llm_response(prompt):
    response = model.invoke(prompt)
    return response.content 


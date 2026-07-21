from langchain_ollama import ChatOllama

# ollama run deepseek-r1 
model = ChatOllama(
    model="deepseek-r1",
    validate_model_on_init=True,
    temperature=0.8 
)

def get_llm_response(prompt):
    response = model.invoke(prompt)
    return response.content 


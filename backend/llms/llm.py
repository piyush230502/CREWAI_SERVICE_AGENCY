import os
from dotenv import load_dotenv
#from langchain_groq import ChatGroq
from litellm import completion
import litellm
litellm.set_verbose = True

load_dotenv()



def get_llms(groq_api_key=None, model_name=None):
    """Return a dict of LLMs for each agent, using the provided API key and model name."""
    if not groq_api_key:
        groq_api_key = os.getenv('GROQ_API_KEY')
    if not model_name:
        model_name = 'groq/gemma2-9b-it'  # Use a Groq-supported model name
    # Ensure model_name is valid for Groq (must match Groq's supported models exactly)
    # Remove any accidental whitespace
    #model_name = model_name.strip()
    # Defensive: ensure groq_api_key is not None or empty
    if not groq_api_key or not isinstance(groq_api_key, str) or not groq_api_key.strip():
        raise ValueError("Groq API key is missing or invalid. Please provide a valid key.")
    return {
        'ceo_llm': completion(model="groq/llama3-8b-8192", 
    messages=[
       {"role": "user", "content": "hello from litellm"}
   ],
),
        'cto_llm': completion(
    model="groq/llama3-8b-8192", 
    messages=[
       {"role": "user", "content": "hello from litellm"}
   ],
),
        'pm_llm': completion(
    model="groq/llama3-8b-8192", 
    messages=[
       {"role": "user", "content": "hello from litellm"}
   ],
),
        'dev_llm': completion(
    model="groq/llama3-8b-8192", 
    messages=[
       {"role": "user", "content": "hello from litellm"}
   ],
),
        'client_llm': completion(
    model="groq/llama3-8b-8192", 
    messages=[
       {"role": "user", "content": "hello from litellm"}
   ],
),
    }

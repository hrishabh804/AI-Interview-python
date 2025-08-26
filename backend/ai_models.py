import os
from openai import OpenAI
import ollama
from dotenv import load_dotenv

load_dotenv()

def ask_openai(question: str) -> str:
    """
    Sends a question to the OpenAI API and returns the answer.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred with OpenAI: {e}"

def ask_ollama(question: str) -> str:
    """
    Sends a question to the Ollama API and returns the answer.
    """
    try:
        response = ollama.chat(
            model='llama2',
            messages=[
                {'role': 'user', 'content': question},
            ],
        )
        return response['message']['content']
    except Exception as e:
        return f"An error occurred with Ollama: {e}. Make sure Ollama is running."

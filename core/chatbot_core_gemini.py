from dotenv import load_dotenv
import google.generativeai as genai
import os
from core.retrieval_langchain import retrieve_context
from core.logging_config import logger

TAG='chatbot_core_gemini.py'
# Load the API key
load_dotenv()
genai_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_response(query):
    # Retrieve relevant context for the query
    context = retrieve_context(query)
    
    # Log the query and context for debugging
    logger.info(f"{TAG}:Query: {query}")
    print(f"{TAG}:Retrieved Context: {context}")

    # Format the prompt to limit the response to the context
    formatted_prompt = (
        f"Use only the information provided in the following context to answer the query.\n\n"
        f"Context:\n{context}\n\n"
        f"Query: {query}\n\n"
        "Answer based strictly on the context above without referencing external information:"
    )
    
    # Generate response using the Gemini API
    chat = model.start_chat(
        history=[
            {"role": "user", "parts": formatted_prompt}
        ]
    )
    response = chat.send_message(query)

    # Log the response for debugging
    logger.info('------------------------------')
    logger.info(f"{TAG}:Generated Response: {response.text}")

    return response.text

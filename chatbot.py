import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# Persona descriptions for system prompts
PERSONA_PROMPTS = {
    "friend": "You are a friendly, supportive companion who speaks casually, offers encouragement, and shares light-hearted banter. Respond with warmth and enthusiasm, like a close friend.",
    "teacher": "You are a knowledgeable, patient educator who explains concepts clearly and concisely. Provide detailed, structured answers with examples, like a dedicated teacher.",
    "sibling": "You are a playful, relatable sibling who teases gently, shares inside jokes, and offers honest advice. Respond with a mix of humor and care, like a brother or sister.",
    "custom": "You are {custom_character}, a character defined by the user. Adopt the personality, tone, and traits described by the user for this character."
}

# Function to get response from Groq API
def get_groq_response(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to get response from Groq API. {str(e)}"

# Streamlit app
st.set_page_config(page_title="Groq Chatbot", page_icon="🤖")
st.title("🤖 PERSONA Chatbot")
st.caption("A fast, AI-powered chatbot powered by Groq")

# Sidebar for persona selection
with st.sidebar:
    st.header("Chatbot Persona")
    persona = st.selectbox(
        "Choose a persona:",
        ["friend", "teacher", "sibling", "custom"],
        index=0
    )
    custom_character = ""
    if persona == "custom":
        custom_character = st.text_input("Specify your custom character (e.g., 'a wise wizard' or 'a sarcastic detective')")
    
    # Button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm ready to chat. What's on your mind?"}]
        st.success("Chat history cleared!")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm ready to chat. What's on your mind?"}]

# Set system prompt based on persona
system_prompt = PERSONA_PROMPTS[persona]
if persona == "custom" and custom_character:
    system_prompt = PERSONA_PROMPTS["custom"].format(custom_character=custom_character)
elif persona == "custom" and not custom_character:
    system_prompt = "You are a helpful assistant with a neutral tone."

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare messages for API (include system prompt)
    api_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.messages
    ]
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        response = get_groq_response(api_messages)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


import streamlit as st
import litellm
from typing import List, Dict
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "github/Phi-4"
if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets["api_key"]


def get_ai_response(messages: List[Dict[str, str]], model: str, api_key: str) -> str:
    """Get response from the AI model using LiteLLM."""
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            api_key=api_key,
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content  # type: ignore
    except Exception as e:
        return f"Error: {str(e)}"


def clear_chat_history():
    """Clear the chat history."""
    st.session_state.messages = []


# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Model input - free text field
    model_input = st.text_input(
        "Model Name:",
        value=st.session_state.model,
        placeholder="e.g., gpt-3.5-turbo, claude-3-sonnet-20240229, gemini-pro",
        help="Enter any model supported by LiteLLM",
    )

    # API Key input
    api_key = st.text_input(
        "API Key:",
        type="password",
        value=st.session_state.api_key,
        help="Enter your API key for the model provider",
    )

    # Update session state
    if model_input != st.session_state.model:
        st.session_state.model = model_input

    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    st.divider()

    # Model suggestions
    st.header("💡 Popular Models")
    st.markdown("""
    **OpenAI:**
    - `gpt-3.5-turbo`
    - `gpt-4`
    - `gpt-4-turbo`
    
    **Anthropic:**
    - `claude-3-sonnet-20240229`
    - `claude-3-haiku-20240307`
    - `claude-3-opus-20240229`
    
    **Google:**
    - `gemini-pro`
    - `gemini-1.5-pro`
    
    **Others:**
    - `ollama/llama2`
    - `together_ai/togethercomputer/llama-2-70b-chat`
    - `replicate/meta/llama-2-70b-chat`
    """)

    st.divider()

    # Chat controls
    st.header("💬 Chat Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_chat_history()
        st.rerun()

    # Chat statistics
    st.header("📊 Chat Stats")
    st.metric("Messages", len(st.session_state.messages))

    # Model info
    st.header("🤖 Model Info")
    st.write(f"**Current Model:** {st.session_state.model}")
    st.write(f"**API Key Set:** {'✅' if st.session_state.api_key else '❌'}")

# Main chat interface
st.title("🤖 AI Chat Assistant")
st.markdown("Chat with various AI models using LiteLLM")

# Check if API key and model are provided
if not st.session_state.api_key or not st.session_state.model:
    st.warning(
        "⚠️ Please enter your API key and model name in the sidebar to start chatting."
    )
    st.info("""
    **How to use:**
    1. Enter any model supported by LiteLLM (see sidebar for examples)
    2. Enter your API key for the corresponding provider
    3. Start chatting!
    
    **LiteLLM supports 100+ models** from providers like OpenAI, Anthropic, Google, 
    Cohere, Replicate, Together AI, Ollama, and many more.
    """)
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"🕐 {message['timestamp']}")

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {"role": "user", "content": prompt, "timestamp": timestamp}
        st.session_state.messages.append(user_message)

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {timestamp}")

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare messages for API (without timestamps)
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]

                response = get_ai_response(
                    api_messages, st.session_state.model, st.session_state.api_key
                )

                st.markdown(response)
                response_timestamp = datetime.now().strftime("%H:%M:%S")
                st.caption(f"🕐 {response_timestamp}")

        # Add assistant response to chat history
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": response_timestamp,
        }
        st.session_state.messages.append(assistant_message)

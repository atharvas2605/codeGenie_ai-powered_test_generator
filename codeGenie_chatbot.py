import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Define the path to your .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the environment variables from the specified file
load_dotenv(dotenv_path)

# -------------------------
# Load Azure OpenAI credentials from environment variables
# -------------------------
AZURE_API_ENDPOINT= os.getenv('API_ENDPOINT')
AZURE_API_KEY= os.getenv('API_KEY')
AZURE_API_VERSION= os.getenv('API_VERSION')
model_temperature = 0.5
model_type = os.getenv('MODEL_TYPE')
model_max_tokens = 16000


if not f"{AZURE_API_KEY}" or not f"{AZURE_API_ENDPOINT}":
    st.error("⚠️ Please set your Azure OpenAI API_KEY and API_ENDPOINT in environment variables.")
    st.stop()

client = AzureOpenAI(
    azure_endpoint=AZURE_API_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION
)
# -------------------------
# Chatbot memory
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# File paths
# -------------------------
GEN_TESTS_DIR = "ai_generated_tests/codeGenie_generated_testcases"
GEN_CODE_DIR = "ai_generated_tests/codeGenie_generated_code"
REFACTORED_LOG = "autofix_code_and_logs/refactored_script_execution.log"
RAW_CODE = "raw_script/generated_code.py"

# -------------------------
# Sidebar file selection
# -------------------------
st.sidebar.header("📂 Chat with codeGenie output")

selected_files = []

if st.sidebar.checkbox("codeGenie: Functional Testcases"):
    if os.path.exists(GEN_TESTS_DIR):
        files = [f for f in os.listdir(GEN_TESTS_DIR) if f.endswith((".py", ".txt"))]
        if files:
            selected = st.sidebar.selectbox("Choose a test document file", files)
            if selected:
                selected_files.append(os.path.join(GEN_TESTS_DIR, selected))

if st.sidebar.checkbox("codeGenie: Refactored Code"):
    if os.path.exists(GEN_CODE_DIR):
        files = [f for f in os.listdir(GEN_CODE_DIR) if f.endswith((".py", ".txt"))]
        if files:
            selected = st.sidebar.selectbox("Choose a refactored code file", files)
            if selected:
                selected_files.append(os.path.join(GEN_CODE_DIR, selected))

if st.sidebar.checkbox("Refactored Script Execution Log"):
    if os.path.exists(REFACTORED_LOG):
        selected_files.append(REFACTORED_LOG)

if st.sidebar.checkbox("Raw Script"):
    if os.path.exists(RAW_CODE):
        selected_files.append(RAW_CODE)

# -------------------------
# Helper: read selected files
# -------------------------
def read_files(files):
    combined = ""
    for file in files:
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # truncate if too long
                if len(content) > 10000:
                    content = content[:10000] + "\n... (truncated)"
                combined += f"\n### {file}\n{content}\n"
        except Exception as e:
            combined += f"\n⚠️ Error reading {file}: {e}\n"
    return combined

# -------------------------
# Chat interface
# -------------------------
st.title("🧞‍♂️ codeGenie Chatbot 💬")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Ask CodeGenie..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build context from selected files
    context_text = ""
    if selected_files:
        context_text = read_files(selected_files)

    # Combine context + user input
    if context_text!="":
        prompt = f"Use the following context from CodeGenie outputs:\n{context_text}\n\nAnswer the user query:\n{user_input}"
    else:
        prompt = f"You are an expert Senior Software Development Engineer in Test. Answer the user query:\n{user_input}"
    # Call Azure OpenAI
    try:
        response = client.chat.completions.create(
            model=model_type,
            temperature=model_temperature,
            max_tokens=model_max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        bot_reply = response.choices[0].message.content.strip()
    except Exception as e:
        bot_reply = f"⚠️ Azure OpenAI call failed: {e}"

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

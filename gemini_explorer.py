import vertexai
import streamlit as st
from vertexai.preview import generative_models
from vertexai.preview.generative_models import GenerativeModel, Part, Content, ChatSession

# Initialize Vertex AI project
project = "my-project-radical-ai-428618"
vertexai.init(project=project)

# Configuration for the generation model
config = generative_models.GenerationConfig(
    temperature=0.4
)

# Load the generative model with the specified configuration
model = GenerativeModel(
    "gemini-pro",
    generation_config=config
)

# Start a chat session
chat = model.start_chat()

# Helper function to display and send Streamlit messages
def llm_function(chat: ChatSession, query, user_name):
    personalized_query = f"{user_name}: {query}"
    response = chat.send_message(personalized_query)
    output = response.candidates[0].content.parts[0].text

    with st.chat_message("model"):
        st.markdown(output)
    st.session_state.messages.append(
        {
            "role": "model",
            "content": output
        }
    )

# Streamlit app title
st.title("Gemini Explorer")

# Capture user name
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if st.session_state.user_name == "":
    st.session_state.user_name = st.text_input("Please enter your name:")

if st.session_state.user_name:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Ensure initial model message if history is empty
    if len(st.session_state.messages) == 0:
        initial_message = f"Hello {st.session_state.user_name}! I am Thor, here to save the day with my super-assistant powers!"
        st.session_state.messages.append(
            {
                "role": "model",
                "content": initial_message
            }
        )
        chat.history.append(
            Content(
                role="model",
                parts=[Part.from_text(initial_message)]
            )
        )

    # Display and load chat history
    for index, message in enumerate(st.session_state.messages):
        content = Content(
            role=message["role"],
            parts=[Part.from_text(message["content"])]
        )
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        if index != 0:  # Avoid re-adding the initial message to history
            chat.history.append(content)

    # For capturing user input
    query = st.chat_input(f"Chat with {st.session_state.user_name}")

    if query:
        # Ensure alternation between user and model messages
        if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
            st.warning("Please wait for the model's response before sending a new message.")
        else:
            with st.chat_message("user"):
                st.markdown(query)
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": query
                }
            )
            try:
                llm_function(chat, query, st.session_state.user_name)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.messages.pop()  # Remove the last user message if it failed

    # Log the state of the chat history for debugging
    st.write("Current chat history:")
    for msg in st.session_state.messages:
        st.write(f"Role: {msg['role']}, Content: {msg['content']}")

    # Log the state of the chat history for the Vertex AI session
    st.write("Vertex AI chat history:")
    for content in chat.history:
        st.write(f"Role: {content.role}, Content: {[part.text for part in content.parts]}")
else:
    st.warning("Please enter your name to start the chat.")

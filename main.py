import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent

st.write("""# Multi Agent Chat Bot using AutoGen Chat Agents""")

class TrackableAssistantAgent(AssistantAgent):
    should_respond = True  # Flag to control response behavior

    def _process_received_message(self, message, sender, silent):
        if self.should_respond:
            with st.chat_message(sender.name):
                st.markdown(message)
        return super()._process_received_message(message, sender, silent)

class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        # Once the assistant has responded, prevent it from further responses
        self.other_agent.should_respond = False
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

selected_model = None
selected_key = None
with st.sidebar:
    st.header("OpenAI Configuration")
    selected_model = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    selected_key = st.text_input("API Key", type="password")

user_input = st.chat_input("Type something...")
if user_input:
    if not selected_key or not selected_model:
        st.warning(
            'You must provide valid OpenAI API key and choose preferred model', icon="⚠️")
        st.stop()

    llm_config = {
        "request_timeout": 100,
        "temperature": 0.7,
        "config_list": [
            {
                "model": selected_model,
                "api_key": selected_key
            }
        ]
    }

    # Create an AssistantAgent instance named "assistant"
    assistant = TrackableAssistantAgent(
        name="assistant", llm_config=llm_config)

    # Create a UserProxyAgent instance named "user"
    user_proxy = TrackableUserProxyAgent(
        name="user", llm_config=llm_config)

    # Link agents to control each other's behavior
    assistant.other_agent = user_proxy
    user_proxy.other_agent = assistant

    # Reset the flag to allow the assistant to respond
    assistant.should_respond = True

    # Create an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Define an asynchronous function
    async def initiate_chat():
        await user_proxy.a_initiate_chat(
            assistant,
            message=user_input,
        )

    # Run the asynchronous function within the event loop
    loop.run_until_complete(initiate_chat())

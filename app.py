import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
from streamlit_extras.stylable_container import stylable_container
from utils.functions import (
    get_vector_store,
    get_context_retriever_chain,
    get_conversational_rag_chain,
    get_response,
    text_to_audio,
    autoplay_audio,
    speech_to_text,
)

# load the variables
load_dotenv()
client = OpenAI()

# app layout
def main():
    # Read HTML file
    st.set_page_config("Vet AI Assistant",page_icon="💼")
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    title = " AI Veterinary  Assistant"
    name = "Mohammed Bahageel"
    profession = "Artificial Intelligence Developer"
    imgUrl = "https://img1.picmix.com/output/pic/normal/9/6/8/7/10757869_6f9dc.gif"
    st.markdown(
                f"""
                <div class="st-emotion-cache-18ni7ap ezrtsby2">
                <img class="profileImage" src="{imgUrl}" alt="Your Photo">
                <div class="textContainer">
                <div class="title"><p>{title}</p></div>
                <p>{name}</p>
                <p>{profession}</p>
                </div>
                </div>
                """,
                unsafe_allow_html=True,
                )
        
    # Float feature initialization
    float_init()

    # Create footer container for the microphone
    footer_container = stylable_container(
        key="Mic_container",
        css_styles=[
            """
            position: absolute;
            bottom: 10px;
            right: 25px;
            background-color: #007bff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: inline-block;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            """
        ],
    )
    user_query = None
    # Create a chat input field
    user_input = st.chat_input("Type your message here...")
    with footer_container:
        transcript = None
        audio_bytes = audio_recorder(text=None, icon_size="15X", key="recorder")
        if audio_bytes:
            # Write the audio bytes to a file
            with st.spinner("Transcribing..."):
                webm_file_path = "temp_audio.mp3"
                with open(webm_file_path, "wb") as f:
                    f.write(audio_bytes)
                transcript = speech_to_text(webm_file_path)
                os.remove(webm_file_path)
                user_query = transcript

    if user_input is not None and user_input != "":
        user_query = user_input
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(
                content="""
                    Welcome to the Veterinary AI Assistant Chat! I am here to help with veterinary medicine questions, 
                    including diagnoses, symptoms, food formulations, surgeries, and more.
                    How can I assist you today? 🥰
                """
                
            )
        ]
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vector_store()
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="🤖"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👩‍⚕️"):
                st.write(message.content)

    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("Human", avatar="👩‍⚕️"):
            st.markdown(user_query)
        with st.chat_message("AI", avatar="🤖"):
            response = st.write_stream(get_response(user_query))
            response_audio_file = "audio_response.mp3"
            text_to_audio(client, response, response_audio_file)
            autoplay_audio(response_audio_file)
            st.session_state.chat_history.append(AIMessage(content=response))
 

    footer_container.float(
        "bottom: 1.5rem; height:30px; width:30px; display:inline-block; align-items:center;justify-content:center; overflow:hidden visible;align-self:self-end;flex-direction: row-reverse;"
    )


if __name__ == "__main__":
    main()

import streamlit as st
from streamlit_custom_chat import ChatContainer
# from custom_chat_bubble import ChatContainer
from streamlit_custom_input import ChatInput
from key_generator.key_generator import generate
from helper_functions import set_bg_hack, set_page_container_style, refresh
  
st.set_page_config(layout="wide")
  
set_bg_hack("streamlit_custom_chat/frontend/src/images/pastel3.jpg") 

set_page_container_style()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#after getting response from bot, add it to session and refresh
def messageFromChatBot(message):
    key = generate()
    st.session_state.messages.append({"role":"assistant","content":message,"key":"assistant-"+key.get_key()})
    refresh('assistant')
    
# st.sidebar.header("header")
# st.sidebar.subheader(‘1.please chose which app you want to operate’)

#if there are no messages in the session add this one
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role":"assistant","content":"Hello! How may I help you?","key":0})
   
col1, col2 = st.columns([2,13]) 
        
with col1:
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    #button to redirect to quiz page (currently does nothing)
    st.button("Take a Quiz", use_container_width=True)
    
with col2:
    #component that displays the messages with adjusted style, remove the styles to see the default style
    ChatContainer(messages=st.session_state.messages, key="chatcontainer", containerStyle={"backgroundColor":"pink"}, bubbleStyle={"textColor":"blue"})

    if st.button(label="assistant", key="assistant"):
        key = generate()
        st.session_state.messages.append({"role": "assistant", "content": "whatever","key":"assistant-"+key.get_key()})
        refresh('assistant')
        
    

    if prompt:= ChatInput(initialValue="",key="inputButton"):
        key = generate()
       
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt,"key":"user-"+key.get_key()})
        # st.session_state.messages.append({"role": "assistant", "content": prompt,"key":"assistant-"+key.get_key()})
        
        #refresh to update ui with new message
        refresh('inputButton')
        
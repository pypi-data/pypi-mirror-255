import streamlit as st
from streamlit_custom_chat import ChatContainer
from streamlit_custom_input import ChatInput
import base64
from key_generator.key_generator import generate

st.set_page_config(layout="wide")

titlecol1, titlecol2, titlecol3 = st.columns([8,5,3])

with titlecol1:
    st.markdown('#')

with titlecol2:
    st.title('Mentor Bot')
    
with titlecol3:
    st.markdown('#')
     
def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "jpg"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         [data-testid="stHeader"] {{
          background-color: rgba(0,0,0,0);
        }}
        [data-testid="baseButton-secondary"]{{
            border-radius:2rem;
            height: 47px;
            border-color: transparent;
            background-color: #fef8ff;
            font-family: 'Itim';
        }}
        [data-testid="baseButton-secondary"]:hover{{
            border-radius:2rem;
            height: 47px;
            border-color: transparent;
            background-color: #fdf4ff;
            color:black;
            font-family: 'Itim';
        }}
        .stChatFloatingInputContainer{{
            background-color: transparent;
        }}
         </style>
         """,
         unsafe_allow_html=True
     )
    
set_bg_hack("streamlit_custom_chat/frontend/src/images/pastel3.jpg") 


def set_page_container_style(
        max_width: int = 1400, max_width_100_percent: bool = False,
        padding_top: int = 2, padding_right: int = 0, padding_left: int = 1, padding_bottom: int = 1,
        # color: str = COLOR, background_color: str = BACKGROUND_COLOR,
    ):
    if max_width_100_percent:
        max_width_str = f'max-width: 100%;'
    else:
        max_width_str = f'max-width: {max_width}px;'
    st.markdown(
        f'''
        <style>
            
            [data-testid="block-container"]{{
                {max_width_str}
                padding-top: {padding_top}rem;
                padding-right: {padding_right}rem;
                padding-left: {padding_left}rem;
                padding-bottom: {padding_bottom}rem;
                
            }}
        </style>
            
        ''',
        unsafe_allow_html=True,
    )

set_page_container_style()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "len" not in st.session_state:
    st.session_state.len = 0

# st.sidebar.header("n")
# st.sidebar.subheader(‘1.please chose which app you want to operate’)

    
if len(st.session_state.messages) ==0:
    st.session_state.messages.append({"role":"assistant","content":"Hello! How may I help you?","key":0})
    st.session_state.messages.append({"role":"user","content":"Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!       Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello!Hello! How may I help you?","key":0})
    
    

col1, col2 = st.columns([2,13]) 

with col1:
    st.markdown("#")
    st.markdown("#")
    st.markdown("#")
    # st.button("Take a Quiz", use_container_width=True)
with col2:
    ChatContainer(messages=st.session_state.messages,key=str(55))

    def refresh(key:str):
        del st.session_state[key]
        st.rerun()

    if answer := ChatInput(initialValue="", key="inputButton"):
        
        # add user message to chat history
        st.session_state.messages.append(
            {"role": "user", "content": answer, "key": "user-"})
        
        st.session_state.userAnswer = answer
        
        # make the rate flag true to send the question to the agent
        st.session_state.rateAnswer = True
        
        # reset question and responding flags
        st.session_state.getQuestion = False
        st.session_state.responding = False
        

            
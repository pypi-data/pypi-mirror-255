# streamlit_custom_chat

![container_example](https://github.com/Farah-S/streamlit_custom_chat/blob/master/streamlit_custom_chat/frontend/public/container_example.png)

Streamlit custom chat messages and container for the chat messages, takes an array of messages for an llm, where each messages can have user or assitant role. The parameters are as follow:

Args:

  messages (list, optional): 
    Messages that will be displayed. Each message must be in the form of 
    {"role":"","content":"","key":""} 
    where the role can be "user" or "assistant", 
    content is the message, 
    key uniquely identifies each messages. 
    Defaults to [].
  
  key (string, optional): 
    uniquely identifies the container instance. Defaults to None.
  
  containerStyle (dict, optional): 
    Allows the customization of the chat container style with CSS. 
    The values that can be changed and their default values are
    
    {
      "overflowY": "auto", 
      "scrollBackgroundColor": "transparent", 
      "borderColor": "transparent",
      "borderRadius": "2rem", 
      "height": "550px", 
      "boxShadow": "inset 0px 0 20px 5px rgb(219 219 219 / 11%), 0px 0px 0px 0px rgb(0 0 0 / 8%), 0px 1px 3px 0px rgb(0 0 0 / 0%)", 
      "backgroundColor": "#fafaff"
      }.
      
  bubbleStyle (dict, optional): 
    Allows the customization of the chat bubble style with CSS. 
    The values that can be changed and their default values are 
    
    {
      textColor:"#534eb1", 
      userBackgroundColor:"rgb(232, 243, 255)", 
      agentBackgroundColor:"#f0efff", 
      paddingRight:"10px", 
      paddingLeft:"10px", 
      paddingBottom:"7px", 
      paddingTop:"7px",
      fontWeight:"525", 
      borderRadius:"2rem", 
      fontFamily:"itim"
    }.

Returns:
  None

## Installation instructions

```sh
pip install streamlit-custom-chat
```

## Usage instructions
Example of how to use without customization

```python
import streamlit as st

from streamlit_custom_chat import ChatContainer

ChatContainer(messages=[{"role":"assistant", "content":"hello!", "key":"0"}], key="")
```

Example of how to use with customization

```python
import streamlit as st

from streamlit_custom_chat import ChatContainer

ChatContainer(messages=[{"role":"assistant", "content":"hello!", "key":"0"}, {"role":"user", "content":"hello!", "key":"1"}], key="", containerStyle={"backgroundColor":"pink"}, bubbleStyle={"userBackgroundColor":"#f0eeef"})
```

For more example please check the app.py

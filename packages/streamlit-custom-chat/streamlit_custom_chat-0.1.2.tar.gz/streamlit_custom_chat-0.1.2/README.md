# streamlit_custom_chat

Streamlit custom chat messages and container for the chat messages, takes an array of messages for an llm, where each messages can have user or assitant role. The parameters are as follow:

messages, key, overflowY, scrollBackgroundColor,
  containerBorderColor,containerBorderRadius, containerHeight,
  containerBoxShadow,
  containerBackgroundColor, textColor, userBackgroundColor, 
  agentBubbleBackgroundColor, bubblePaddingRight, bubblePaddingLeft, 
  bubblePaddingBottom, bubblePaddingTop,
  fontWeight, bubbleBorderRadius, fontFamily

## Installation instructions

```sh
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps streamlit_custom_chat
```

## Usage instructions

```python
import streamlit as st

from streamlit_custom_chat import ChatContainer

value = ChatContainer(messages=[], key="")
```

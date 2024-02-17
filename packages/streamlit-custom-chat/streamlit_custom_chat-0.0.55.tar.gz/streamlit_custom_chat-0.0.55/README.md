# streamlit_custom_chat

Streamlit custom chat messages and container for the chat messages, takes an array of messages for an llm, where each messages can have user or assitant role and the array is configured as [{"role":"user", "content":"", "key":""}, {"role":"assistant", "content":"", "key":""}]

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

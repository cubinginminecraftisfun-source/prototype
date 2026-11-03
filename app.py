import os
import threading
from datetime import datetime

import qrcode
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="QR Chatroom",
    page_icon="💬",
    layout="centered",
)

# Shared in-memory state for visitors using this running app process.
# Messages disappear when the server process restarts.
@st.cache_resource
def get_chat_store():
    return {
        "messages": [],
        "lock": threading.Lock(),
    }


chat_store = get_chat_store()

st.title("💬 QR Chatroom")
st.caption("A simple shared chatroom. Messages are temporary.")

# QR code setup: use your deployed Streamlit URL here.
with st.sidebar:
    st.header("Share this chatroom")
    app_url = st.text_input(
        "Public app URL",
        value=os.getenv("APP_URL", ""),
        placeholder="https://your-app-name.streamlit.app",
        help="After deploying, paste your public Streamlit URL here.",
    )

    if app_url.strip():
        qr_image = qrcode.make(app_url.strip())
        st.image(qr_image, caption="Scan to open this chatroom", use_container_width=True)
        st.code(app_url.strip(), language=None)
    else:
        st.info("Add your deployed app URL to create its QR code.")

# Simple name entry
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.username:
    st.subheader("Join the conversation")
    name = st.text_input("Choose a display name", max_chars=24)

    if st.button("Join chat", type="primary", use_container_width=True):
        cleaned_name = name.strip()
        if cleaned_name:
            st.session_state.username = cleaned_name
            st.rerun()
        else:
            st.warning("Please enter a display name.")
    st.stop()

st.write(f"Posting as **{st.session_state.username}**")
if st.button("Change display name"):
    st.session_state.username = ""
    st.rerun()

# Refresh the page periodically so visitors see messages from others.
st_autorefresh(interval=2000, key="chat_refresh")

st.subheader("Messages")

with chat_store["lock"]:
    visible_messages = list(chat_store["messages"])

if not visible_messages:
    st.info("No messages yet. Start the conversation!")

for message in visible_messages:
    with st.chat_message("user"):
        st.markdown(f"**{message['username']}**")
        st.write(message["text"])
        st.caption(message["time"])

prompt = st.chat_input("Write a message...")
if prompt and prompt.strip():
    new_message = {
        "username": st.session_state.username,
        "text": prompt.strip(),
        "time": datetime.now().strftime("%H:%M"),
    }

    with chat_store["lock"]:
        chat_store["messages"].append(new_message)

    st.rerun()

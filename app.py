# app.py
import streamlit as st
from core.chatbot_core_gemini import generate_response

# Streamlit app setup
st.title("GitLab Handbook Chatbot")

if 'history' not in st.session_state:
    st.session_state.history = []

# Create a text input field and monitor for changes
user_query = st.text_input("Ask a question about GitLab:", key="user_query")

# Check if the submit button is clicked or the Enter key is pressed
if st.button("Submit") or st.session_state.get("user_query_submitted", False):
    if user_query:
        # Generate response with retrieved context
        response = generate_response(user_query)
        st.session_state.history.append({"user": user_query, "response": response})
        
        # Clear the Enter key flag to prevent duplicate submissions
        st.session_state["user_query_submitted"] = False
        
        # Display chat history
        for interaction in st.session_state.history:
            st.write(f"**You:** {interaction['user']}")
            st.write(f"**Bot:** {interaction['response']}")
    else:
        st.write("Please enter a question.")

# Update the session state when Enter is pressed
if st.session_state.get("user_query", ""):
    if st.session_state["user_query"] != "":
        st.session_state["user_query_submitted"] = True

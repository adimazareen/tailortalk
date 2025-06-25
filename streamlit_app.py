import streamlit as st
import requests
import json

# Set up the page
st.title("TailorTalk - Appointment Booking Assistant")
st.write("I can help you schedule appointments on my calendar. Try saying things like:")
st.write("- 'I want to schedule a call for tomorrow afternoon'")
st.write("- 'Do you have any free time this Friday?'")
st.write("- 'Book a meeting between 3-5 PM next week'")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How can I help you schedule an appointment?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        try:
            # Call FastAPI backend
            response = requests.post(
                "http://localhost:8000/chat",
                json={"text": prompt}
            )
            response.raise_for_status()
            response_data = response.json()
            assistant_response = response_data.get("response", "I didn't understand that.")
        except Exception as e:
            assistant_response = f"Sorry, I encountered an error: {str(e)}"
        
        st.markdown(assistant_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
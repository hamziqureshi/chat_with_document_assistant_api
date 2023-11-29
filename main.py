import openai
import time
import streamlit as st

def clear_submit():
    st.session_state["submit"] = False

def main():
    url = "https://www.linkedin.com/in/hamzaakramqureshi/"
    st.markdown('<h1>Chat with your File' , unsafe_allow_html=True)
    st.markdown('<h3>Developed with Assitant API from OpenAI GPT </h3>', unsafe_allow_html=True)
    st.markdown("Author: [Hamza Akram](%s)" % url)


    # Sidebar
    index = None
    doc = None
    with st.sidebar:
        user_secret = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",
            value=st.session_state.get("OPENAI_API_KEY", ""),
        )

        uploaded_file = st.file_uploader(
            "Upload a pdf, docx, or txt file",
            type=["pdf", "docx", "txt"],
            help="Scanned documents are not supported yet!",
            on_change=clear_submit,
        )

        if uploaded_file is not None:         
            if 'client' not in st.session_state:
                # Initialize the client
                st.session_state.client = openai.OpenAI(api_key=user_secret)

                st.session_state.file = st.session_state.client.files.create(
                    file = uploaded_file,
                    purpose='assistants'
                )

                # Step 1: Create an Assistant
                st.session_state.assistant = st.session_state.client.beta.assistants.create(
                    name="Chat with Document",
                    instructions="You are a chatbot that gives answer related to document provided. Use your knowledge base to best respond to queries. Striclty answer related to documents and if you can't find answer in the uploaded file then say that 'I can not find answer in the documents.'",
                    model="gpt-4-1106-preview",
                    file_ids=[st.session_state.file.id],
                    tools=[{"type": "retrieval"}]
                )

                # Step 2: Create a Thread
                st.session_state.thread = st.session_state.client.beta.threads.create()

    
    tab1, tab2 = st.tabs(["Chat with the File", "About the Application"])
    with tab1:
        if 'generated' not in st.session_state:
            st.session_state['generated'] = []

        if 'past' not in st.session_state:
            st.session_state['past'] = []

        def get_text():
            if user_secret:
                st.header("Ask me something about the document:")
                input_text = st.text_area("You:", on_change=clear_submit)
                return input_text
        user_input = get_text()

        button = st.button("Submit")

        if button or st.session_state.get("submit"):
            if not user_input:
                st.error("Please enter a question!")
            else:
                st.session_state["submit"] = True
                message = st.session_state.client.beta.threads.messages.create(
                thread_id=st.session_state.thread.id,
                role="user",
                content=user_input
                )

                run = st.session_state.client.beta.threads.runs.create(
                thread_id=st.session_state.thread.id,
                assistant_id=st.session_state.assistant.id,
                instructions="Striclty answer related to documents and if you can't find answer in the uploaded file then say that 'I can not find answer in the documents.'"
                )

                while True:
                    # Wait for 5 seconds
                    time.sleep(5)

                    # Retrieve the run status
                    run_status = st.session_state.client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread.id,
                    run_id=run.id
                    )
                    

                    # If run is completed, get messages
                    if run_status.status == 'completed':
                        messages = st.session_state.client.beta.threads.messages.list(
                        thread_id=st.session_state.thread.id
                        )

                        # Loop through messages and print content based on role
                        for msg in messages.data:
                            role = msg.role
                            content = msg.content[0].text.value
                            st.write(f"{role.capitalize()}: {content}")
                            st.session_state.past.append(user_input)
                            st.session_state.generated.append(content)
                        break
                    else:
                        st.write("Waiting for the Assistant to process...")
                        time.sleep(5)

                    
                    if st.session_state['generated']:
                        for i in range(len(st.session_state['generated'])-1, -1, -1):
                            message(st.session_state["generated"][i], key=str(i))
                            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

    with tab2:
        st.write('About the Application')
        st.write('Chat with Files enables user to extract all the information from a file. User can obtain the transcription and also ask questions to the file through a chat.')
        st.write('Features include- ')
        st.write('1. Reading any pdf, docx, txt file')
        st.write('2. Chatting with the file using streamlit-chat and assistant api from openai GPT')
    
if __name__ == "__main__":
    main()

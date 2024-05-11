import os
import openai
import streamlit as st
from dotenv import load_dotenv
from render import *
from utils import *
import prompts
from pinecone import Pinecone
from langchain_groq import ChatGroq
from groq import Groq
import faiss
import time
import pymongo

# --- LOAD ENVIRONMENT VARIABLES --- # 
load_dotenv()


# --- SET PAGE CONFIG --- # 
st.set_page_config(page_title="AmbroiseGPT", page_icon=":world_map:", initial_sidebar_state="collapsed") #  🛡️	:shield:


# --- LOAD CSS STYLE --- # 
with open('./styles/style.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# --- DISABLE SIDEBAR TOGGLE --- # 
# st.markdown(
#     """
# <style>
#     [data-testid="collapsedControl"] {
#         display: none
#     }
# </style>
# """,
#     unsafe_allow_html=True,
# )

# --- LOAD OPENAI API KEY --- # 
openai.api_key = os.getenv("OPENAI_API_KEY")


# --- LOAD GROQ API KEY --- # 
groq.api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq = Groq(api_key=groq.api_key)


# --- LOAD PINECONE API KEY --- # 
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


# --- LOAD PINECONE INDEX --- # 
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

# --- CONNECT TO MONGODB --- # 
client = pymongo.MongoClient(os.getenv("MONGO_DB"))
db = client["your_database"]
collection = db["chat_history"]


### ------ ////// AMBROISE GPT MAIN APP \\\\\\ ------ #### 

# Define chat history storage and track if a query has been submitted
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.submitted_query = False  # Track if the user has submitted a query


# Display avatar and description only if no query has been submitted
if not st.session_state.submitted_query:
    # --- PAGE LAYOUT --- # 
    # Split Page into 2 columns
    col1, col2 = st.columns([1, 3])

    # --- LEFT COLUMN --- # 
    # AmbroiseGPT Avatar
    with col1:
        st.write("")
        col1.image(
            "assets/Ambroise_Debret.png",
            # Manually Adjust the width of the image as per requirement
        )

    # --- RIGHT COLUMN --- #  
    # Name of the GPT
    with col2:
        col1a, col2a = st.columns([0.01, 10000])    
        col2a.header("🗺️ AmbroiseGPT") # 

        # AmbroiseGPT - Descriptive introduction for user 
        col2a.write("Salut ! Je suis AmbroiseGPT, votre assistant IA en freelancing/digital nomadisme. J'ai été entraîné sur les vidéos de ma chaine YouTube + les pages de [mon site internet](https://ambroisedebret.com/) dédiés au lifestyle digital nomade. Posez-moi vos questions, et je ferai de mon mieux pour y répondre en vous fournissant les liens de sources complémentaires pour approfondir le sujet.")


# Sidebar for model selection
model_options = ["OpenAI - GPT-3.5-turbo", "Groq - Mixtral-8x7b-32768"]
selected_model = st.sidebar.selectbox("Select Model", model_options, index=0, disabled=True)




# Construct messages from chat history
def construct_messages(history):
    messages = [{"role": "system", "content": prompts.system_message}]
    
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    
    return messages


# Generate response to user prompt
def generate_response():
    # Set submitted_query to True after the first query submission
    st.session_state.submitted_query = True

    # Append user's query to chat history
    st.session_state.history.append({
        "message": st.session_state.prompt,
        "is_user": True,
    })
    

    print(f"Query: {st.session_state.prompt}")
    unique_sources = set()  # Use a set to store unique source titles
    
    # Perform semantic search and format results
    search_results = semantic_search(st.session_state.prompt, index, top_k=3)

    print(f"Results: {search_results}")

    context = ""
    for i, (title, transcript, source) in enumerate(search_results):
        context += f"Snippet from: {title}\n {transcript}\n\n"
        unique_sources.add(source)  # Add unique source urls to the set

    # Convert set of unique sources to a formatted string
    # sources_text = "Source(s): " + ", ".join(f"[{source}]({source})" for source in unique_sources)
    # sources_text = "Source(s): " + ", ".join(f"[{source}](https://bit.ly/cybersecurity-best-practice-guide)" for source in unique_sources)
    sources_text = "</br>" + "Source(s): " + ", ".join(f"[{source}]({source})" for source in unique_sources)
    # sources_text = "</br>" + "Source(s): " + ", ".join(f"[{source}]({source}?utm_medium=&utm_source=affiliate-mc&utm_campaign=affiliate-mc-bekkaye&utm_content=&utm_keyword=&source=affiliate&campagne=affiliate-mc-bekkaye)" for source in unique_sources)
    

    # Generate human prompt template and convert to API message format
    query_with_context = prompts.human_template.format(query=st.session_state.prompt, context=context)

    
        # --- PAGE LAYOUT --- # 
    # Split Page into 2 columns
    col1, col2 = st.columns([1,3])

    # --- LEFT COLUMN --- # 
    # AmbroiseGPT Avatar
    with col1:
        st.write("")
        col1.image(
                "assets/Ambroise_Debret.png",
                # Manually Adjust the width of the image as per requirement
                )

    # --- RIGHT COLUMN --- #  
    # Name of the GPT
    with col2:
        col1a, col2a = st.columns([0.01,10000])    
        col2a.header("🗺️ AmbroiseGPT") # 

    # AmbroiseGPT - Descriptive introduction for user 
    with col2:
        col1a, col2a = st.columns([1,100])
        col2a.write("Salut ! Je suis AmbroiseGPT, votre assistant IA en freelancing/digital nomadisme. J'ai été entraîné sur les vidéos de ma chaine YouTube + les pages de [mon site internet](https://ambroisedebret.com/) dédiés au lifestyle digital nomade. Posez-moi vos questions, et je ferai de mon mieux pour y répondre en vous fournissant les liens de sources complémentaires pour approfondir le sujet.")


    # Create chat history messages
    messages = [{"role": "system", "content": prompts.system_message}]
    for entry in st.session_state.history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    messages.append({"role": "user", "content": query_with_context})

    # Run the LLMChain
    # response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    
    # response = Groq(api_key=groq.api_key).chat.completions.create(model="mixtral-8x7b-32768", messages=messages)
    # print(messages)

    # Generate response from Groq API
    # print("API Endpoint:", groq.chat.completions.api_endpoint)  # Add this line to print the API endpoint
    
    # response = groq.chat.completions.create(
    #     model="mixtral-8x7b-32768",
    #     messages=messages,
    # )
    
    # Determine which model to use for response generation
    if selected_model == "OpenAI - GPT-3.5-turbo":
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=True)

    elif selected_model == "Groq - Mixtral-8x7b-32768":
        response = groq.chat.completions.create(model="mixtral-8x7b-32768", messages=messages, stream=True)

    # response = groq.chat.completions.create(
    #     # model="mixtral-8x7b-32768",
    #     model="llama3-8b-8192",
    #     messages=messages,
    #     stream=True,
    #     # max_tokens= 1000,
    #     # temperature=0.7,
        
    # )

    # ChatGroq()

    print(f"Response : {response}")

     # Display user input and bot responses sequentially
    for message in st.session_state.history:
        if message["is_user"]:
            st.write(user_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)
        else:
            st.write(bot_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)

    # Create an empty placeholder for the bot's response
    bot_response_placeholder = st.empty()
    
    # Initialize an empty string to accumulate the bot's response
    bot_response_with_sources = ""

    # Stream the response and display incremental updates
    for chunk in response:
        if selected_model == "OpenAI - GPT-3.5-turbo":
            for chunk in response:
                # Check if 'choices' key exists and it's a non-empty list
                if 'choices' in chunk and isinstance(chunk['choices'], list) and len(chunk['choices']) > 0:
                    # Check if 'delta' key exists in the first choice and it's a dictionary
                    if 'delta' in chunk['choices'][0] and isinstance(chunk['choices'][0]['delta'], dict):
                        # Access 'content' attribute if available, otherwise use an empty string
                        content = chunk['choices'][0]['delta'].get('content', '')

                        # Append the content to the accumulated response
                        bot_response_with_sources += content

                        # Update the bot response placeholder with the latest response
                        bot_response_placeholder.markdown(
                            # bot_msg_container_html_template.replace("$MSG", f"{bot_response_with_sources}▌"),
                            bot_msg_container_html_template.replace("$MSG", bot_response_with_sources + " ▌"),
                            unsafe_allow_html=True
                        )

                        # Introduce a delay for typing effect (adjust as needed)
                        time.sleep(0.025)

        elif selected_model == "Groq - Mixtral-8x7b-32768":
            bot_response_with_sources += chunk.choices[0].delta.content or ""  # Example, assuming 'message' holds the bot response in Groq response


        # Update bot response placeholder with the latest response
        bot_response_placeholder.markdown(
            # bot_msg_container_html_template.replace("$MSG", f"{bot_response_with_sources}▌"),
            bot_msg_container_html_template.replace("$MSG", bot_response_with_sources + " ▌"),
            unsafe_allow_html=True
        )

        # Introduce a delay for typing effect (adjust as needed)
        time.sleep(0.025)

    # Display sources after bot's response is fully typed
    bot_response_placeholder.markdown(
        bot_msg_container_html_template.replace("$MSG", bot_response_with_sources + "\n\n" + sources_text),
        unsafe_allow_html=True
    )

    # Append bot response to chat history
    st.session_state.history.append({
        "message": bot_response_with_sources + "\n\n" + sources_text,
        "is_user": False
    })

    # Append bot response to chat history
    chat_entry = {
        "user_message": st.session_state.prompt,
        "bot_response": bot_response_with_sources,
        "timestamp": time.time()  # Add timestamp if needed
    }
    
    # Save chat history to MongoDB
    collection.insert_one(chat_entry)

    # Clear the input prompt after processing
    st.session_state.prompt = ''


# User input prompt
user_prompt = st.text_input(
    " ",
    key="prompt",
    placeholder="Écrivez votre message...",
    on_change=generate_response,
)

# COPYRIGHT
st.markdown(
    "<div style='text-align: right; color: #83858C; font-size:14px;'>&copy; 2024 Copyright <a href='https://ambroisedebret.com/masterclass-formation-freelance-gratuite/?utm_medium=&utm_source=affiliate-mc&utm_campaign=affiliate-mc-bekkaye&utm_content=&utm_keyword=&source=affiliate&campagne=affiliate-mc-bekkaye'>Ambroise Debret</a> - All rights reserved.</div>",
    unsafe_allow_html=True
)
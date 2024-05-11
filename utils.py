import os
import openai
import streamlit as st
from dotenv import load_dotenv
import groq
import faiss

# --- LOAD ENVIRONMENT VARIABLES --- # 
load_dotenv()


# --- LOAD API KEYS --- # 

# Load OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- LOAD GROQ API KEY --- # 
groq.api_key = os.getenv("GROQ_API_KEY")

# Load PINECONE_API_KEY
api_key_pinecone = os.getenv("PINECONE_API_KEY")

# Set up PINECONE_ENVIRONMENT
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

# Set up PINECONE_ENDPOINT
pinecone_endpoint = os.getenv("PINECONE_ENDPOINT")



# --- RETRIEVAL AUGMENTED GENERATION --- # 

# Create embeddings from user query & AmbroiseGPT reponses 
# def get_embeddings_openai(text):
#     try:
#         response = openai.Embedding.create(
#             input=text,
#             model="text-embedding-ada-002"
#         )
#         # response = groq.Embedding.create(
#         #     input=text,
#         #     model="text-embedding-ada-002"
#         # )
#         response = response['data']
#         return [x["embedding"] for x in response]
#     except Exception as e:
#         print(f"Error in get_embeddings_openai: {e}")
#         raise


# def get_embeddings_faiss(text):
#     try:
#         response = openai.Embedding.create(
#             input=text,
#             model="text-embedding-ada-002"
#         )
#         # response = groq.Embedding.create(
#         #     input=text,
#         #     model="text-embedding-ada-002"
#         # )
#         response = response['data']
#         return [x["embedding"] for x in response]
#     except Exception as e:
#         print(f"Error in get_embeddings_openai: {e}")
#         raise

def get_embeddings_faiss(text):
    try:
        # Generate or retrieve embeddings compatible with Faiss
        # Example: Use OpenAI API to obtain text embeddings
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-3-small"
        )
        embeddings = [x["embedding"] for x in response['data']]
        return embeddings
    except Exception as e:
        print(f"Error in get_embeddings_faiss: {e}")
        raise




def initialize_faiss_index(embeddings):
    try:
        d = len(embeddings[0])  # Dimension of the embeddings
        index = faiss.IndexFlatL2(d)  # Initialize a flat index with L2 distance
        index.add(embeddings)  # Add your embeddings to the index
        return index
    except Exception as e:
        print(f"Error in initialize_faiss_index: {e}")
        raise




# Semantic search in PINECONE Database
# def semantic_search(query, index, **kwargs):
#     try:
#         xq = get_embeddings_openai(query)

#         xr = index.query(vector=xq[0], top_k=kwargs.get('top_k', 3), include_metadata=kwargs.get('include_metadata', True))

#         if xr.error:
#             print(f"Invalid response: {xr}")
#             raise Exception(f"Query failed: {xr.error}")

#         titles = [r["metadata"]["video_title"] for r in xr["matches"]]
#         transcripts = [r["metadata"]["text"] for r in xr["matches"]]
#         sources = [r["metadata"]["video_url"] for r in xr["matches"]] # Add sources
#         return list(zip(titles, transcripts, sources))
    
    

#     except Exception as e:
#         print(f"Error in semantic_search: {e}")
#         raise


def semantic_search(query, index, **kwargs):
    try:
        xq = get_embeddings_faiss(query)  # Get embeddings for the query

        xr = index.query(vector=xq[0], top_k=kwargs.get('top_k', 3), include_metadata=kwargs.get('include_metadata', True)) # Search for nearest neighbors

        if xr.error:
            print(f"Invalid response: {xr}")
            raise Exception(f"Query failed: {xr.error}")

        titles = [r["metadata"]["video_title"] for r in xr["matches"]]
        transcripts = [r["metadata"]["text"] for r in xr["matches"]]
        sources = [r["metadata"]["video_url"] for r in xr["matches"]] # Add sources
        return list(zip(titles, transcripts, sources))
    
    

    except Exception as e:
        print(f"Error in semantic_search: {e}")
        raise

# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict
import faiss
import numpy as np
import json
from PyPDF2 import PdfReader
import tiktoken

app = FastAPI()
client = OpenAI()

# Allow CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ensure directories exist
os.makedirs('uploaded_files', exist_ok=True)

# Global variables (in production, use a database)
embedding_dimension = 1536  # For text-embedding-ada-002
index = faiss.IndexFlatL2(embedding_dimension)
document_chunks = []

# Try to load existing index and document chunks
if os.path.exists('vector_index.faiss'):
    index = faiss.read_index('vector_index.faiss')
    with open('document_chunks.json', 'r') as f:
        document_chunks = json.load(f)

class ChatRequest(BaseModel):
    message: str

class GuardrailsRequest(BaseModel):
    settings: str

def extract_text_from_file(file_path):
    text = ''
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    elif file_path.endswith('.docx'):
        text = docx2txt.process(file_path)
    else:
        # Use Tika for other file types
        raw = parser.from_file(file_path)
        text = raw['content']
    return text

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")

    response = client.embeddings.create(
        input=text,
        model=model
    )
    # print(response)
    embedding = response.data[0].embedding
    return embedding

def split_text_into_chunks(text, max_tokens=500):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk)
        chunks.append(chunk_text)
    return chunks

@app.post("/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    try:
        file_location = f"uploaded_files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())

        # Extract text from the file
        text = extract_text_from_file(file_location)

        # Split text into chunks
        chunks = split_text_into_chunks(text)

        # Generate embeddings for each chunk and add to index
        for chunk in chunks:
            embedding = get_embedding(chunk)
            document_chunks.append({'text': chunk, 'embedding': embedding})
            vector = np.array(embedding, dtype='float32')
            vector = np.expand_dims(vector, axis=0)
            index.add(vector)

        # Save index and document chunks
        faiss.write_index(index, 'vector_index.faiss')
        with open('document_chunks.json', 'w') as f:
            json.dump(document_chunks, f)

        return {"message": f"File '{file.filename}' uploaded and processed successfully."}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading and processing the file.")


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    student_message = request.message
    # client = OpenAI()
    # Load guardrails (if any)
    guardrails = ''
    if os.path.exists('guardrails.txt'):
        with open('guardrails.txt', 'r') as f:
            guardrails = f.read()

    
#     from openai import OpenAI
# client = OpenAI()

# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {
#             "role": "user",
#             "content": "Write a haiku about recursion in programming."
#         }
#     ]
# )

# print(completion.choices[0].message)
    try:
        # Generate embedding for the student's query
        # Generate embedding for the student's query
        query_embedding = get_embedding(student_message)
        query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
        # query_vector = np.expand_dims(query_vector, axis=0)
        query_vector = query_embedding

        # Retrieve top k relevant chunks
        k = 5
        distances, indices = index.search(query_vector, k)
        print(f"Indices: {indices}")
        print(f"Indices shape: {indices.shape}")
        print(f"Number of document chunks: {len(document_chunks)}")

        # Handle case where no results are returned
        if indices.size == 0 or indices.shape[1] == 0:
            return {"reply": "I'm sorry, I couldn't find any relevant information to answer your question."}

        retrieved_text = ''
        for idx in indices[0]:
            if idx < len(document_chunks):
                retrieved_text += document_chunks[idx]['text'] + '\n'
            else:
                print(f"Index {idx} is out of bounds for document_chunks with length {len(document_chunks)}")

        # Construct the prompt
        prompt = f"""{guardrails}

Use the following information to answer the question.

Information:
{retrieved_text}

Question:
{student_message}

Answer:"""
        # Build the messages list for the ChatCompletion
        messages = [
            {"role": "system", "content": f"{guardrails}\nYou are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        # Call the OpenAI ChatCompletion API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use "gpt-4" if you have access
            messages=messages
        )
        # reply = completion.choices[0].message['content'].strip()
        reply = completion.choices[0].message
        #console.log(reply)
        return {"reply": reply}
    except Exception as e:
        # Handle errors
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the response.")

@app.post("/guardrails")
async def guardrails_endpoint(request: GuardrailsRequest):
    try:
        with open('guardrails.txt', 'w') as f:
            f.write(request.settings)
        return {"message": "Guardrails saved successfully."}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while saving guardrails.")

@app.post("/upload")
async def upload_endpoint(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_location = f"uploaded_files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        print(f"File saved at {file_location}")

        # Extract text from the file
        text = extract_text_from_file(file_location)
        if text:
            print(f"Extracted text length: {len(text)}")
        else:
            print("No text extracted from the file.")

        # Split text into chunks
        chunks = split_text_into_chunks(text)
        print(f"Number of chunks created: {len(chunks)}")

        # Generate embeddings for each chunk and add to index
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            vector = np.array(embedding).astype('float32')
            vector = vector.reshape(1, -1)
            index.add(vector)
            document_chunks.append({'text': chunk, 'embedding': embedding})
            print(f"Added chunk {i} to index and document_chunks")

        # Save index and document chunks if needed
        # ...

        return {"message": f"File '{file.filename}' uploaded and processed successfully."}
    except Exception as e:
        print(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading and processing the file.")

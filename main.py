# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI

app = FastAPI()

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

class ChatRequest(BaseModel):
    message: str

class GuardrailsRequest(BaseModel):
    settings: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    student_message = request.message
    client = OpenAI()
    # Load guardrails (if any)
    guardrails = ''
    if os.path.exists('guardrails.txt'):
        with open('guardrails.txt', 'r') as f:
            guardrails = f.read()

    # Build the messages list for the ChatCompletion
    messages = [
        {"role": "system", "content": f"{guardrails}\nYou are a helpful assistant."},
        {"role": "user", "content": student_message}
    ]
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
        file_location = f"uploaded_files/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        return {"message": f"File '{file.filename}' uploaded successfully."}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading the file.")

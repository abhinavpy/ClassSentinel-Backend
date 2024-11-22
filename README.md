# Learning Assistant Backend

This repository contains the backend code for the Learning Assistant application, which provides AI-powered assistance to students based on documents uploaded by instructors. The backend is built using FastAPI and integrates with OpenAI's GPT-3.5-turbo model and embedding models to facilitate Retrieval-Augmented Generation (RAG).

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [Upload Endpoint (`/upload`)](#upload-endpoint-upload)
  - [Chat Endpoint (`/chat`)](#chat-endpoint-chat)
  - [Guardrails Endpoint (`/guardrails`)](#guardrails-endpoint-guardrails)
- [Testing the Application](#testing-the-application)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)
- [License](#license)

---

## Features

- **Document Uploading**: Instructors can upload documents (PDFs, DOCX) which are processed and used to assist students.
- **Text Extraction**: Extracts text from uploaded documents for processing.
- **Embedding Generation**: Generates embeddings using OpenAI's `text-embedding-3-small` model.
- **Vector Similarity Search**: Utilizes FAISS for efficient similarity search over embeddings.
- **Retrieval-Augmented Generation (RAG)**: Answers student queries based on the uploaded documents.
- **Guardrails Configuration**: Instructors can set guidelines or guardrails to influence the assistant's responses.

---

## Prerequisites

- **Python 3.7 or higher**
- **An OpenAI API Key**: You can obtain one from [OpenAI's website](https://platform.openai.com/account/api-keys).
- **pip**: Python package installer.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/learning-assistant-backend.git
cd learning-assistant-backend
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:

  ```bash
  venv\Scripts\activate
  ```

- On macOS/Linux:

  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, you can install the dependencies directly:

```bash
pip install fastapi uvicorn openai python-multipart PyPDF2 docx2txt tika faiss-cpu numpy tiktoken python-dotenv
```

**Note**: Ensure that Java is installed on your system, as it's required by the `tika` library for text extraction from various file types.

---

## Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the root directory to store your environment variables securely.

```bash
touch .env
```

Add your OpenAI API key to the `.env` file:

```
OPENAI_API_KEY=your-openai-api-key
```

Replace `your-openai-api-key` with your actual API key from OpenAI.

### 2. Ensure Necessary Directories Exist

The application uses the following directories:

- `uploaded_files/`: To store uploaded documents.
- `vector_index.faiss`: To store the FAISS index (if you persist it).
- `document_chunks.json`: To store document chunks (if you persist them).

Ensure that the `uploaded_files` directory exists:

```bash
mkdir uploaded_files
```

---

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

- The `--reload` flag enables auto-reload on code changes.
- The application will run on `http://127.0.0.1:8000` by default.

---

## API Endpoints

### Upload Endpoint (`/upload`)

- **Method**: `POST`
- **Description**: Uploads a document, extracts text, generates embeddings, and adds them to the vector index.
- **Parameters**:
  - `file`: The document file to upload (supports PDF and DOCX).
- **Usage**:

  ```bash
  curl -X POST "http://127.0.0.1:8000/upload" \
    -F "file=@/path/to/your/document.pdf"
  ```

### Chat Endpoint (`/chat`)

- **Method**: `POST`
- **Description**: Handles student queries, performs similarity search on embeddings, and generates responses using OpenAI's GPT-3.5-turbo model.
- **Parameters**:
  - `message`: The student's query.
- **Usage**:

  ```bash
  curl -X POST "http://127.0.0.1:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{
      "message": "Can you explain quantum entanglement?"
    }'
  ```

### Guardrails Endpoint (`/guardrails`)

- **Method**: `POST`
- **Description**: Allows instructors to set guardrails or guidelines for the assistant's responses.
- **Parameters**:
  - `settings`: A string containing the guardrails instructions.
- **Usage**:

  ```bash
  curl -X POST "http://127.0.0.1:8000/guardrails" \
    -H "Content-Type: application/json" \
    -d '{
      "settings": "Provide explanations suitable for high school students."
    }'
  ```

---

## Testing the Application

### 1. Upload a Document

- Use the Instructor Interface (if available) or the `/upload` endpoint to upload a document.
- Supported file types: PDF, DOCX.

### 2. Ask a Question

- Use the Student Interface (if available) or the `/chat` endpoint to send a query.
- The assistant should provide a response based on the uploaded document.

### 3. Verify Responses

- Ensure that the assistant's responses are accurate and incorporate information from the uploaded documents.
- If guardrails are set, verify that the responses adhere to them.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors (e.g., `ModuleNotFoundError`)

- **Cause**: Missing dependencies.
- **Solution**: Install all required packages using `pip install -r requirements.txt`.

#### 2. `OPENAI_API_KEY` Not Found

- **Cause**: API key not set or `.env` file not configured.
- **Solution**: Ensure your `.env` file is set up correctly with your OpenAI API key.

#### 3. Errors During File Upload

- **Cause**: Unsupported file type or issues with text extraction.
- **Solution**:
  - Ensure the file is a supported format (PDF or DOCX).
  - Check that all text extraction libraries (`PyPDF2`, `docx2txt`, `tika`) are installed.
  - Verify that Java is installed if using `tika`.

#### 4. "List Index Out of Range" Error When Chatting

- **Cause**: No embeddings in the index or `document_chunks` is empty.
- **Solution**:
  - Confirm that documents have been uploaded and processed successfully.
  - Check that embeddings are generated and added to the index.
  - Ensure `document_chunks` is populated.

#### 5. OpenAI API Errors

- **Cause**: Issues with the API request, such as exceeding token limits or invalid inputs.
- **Solution**:
  - Check that your API key is valid and has sufficient quota.
  - Verify that input texts are within the allowed token limits.

### Logging and Debugging

- The application prints debug statements to the console.
- Review the terminal output where the backend server is running to identify errors.
- Add additional `print` statements in the code if needed to trace execution.

---

## Additional Notes

### Using a Vector Database

For scalability, consider using an external vector database like Pinecone or Weaviate instead of FAISS. These databases handle embedding storage and similarity search more efficiently, especially for large datasets.

### Environment Variables

- **Security**: Do not commit your `.env` file or API keys to version control.
- **Customization**: You can add other environment variables as needed (e.g., for database connection strings).

### Dependencies Management

- Keep your `requirements.txt` updated when adding new dependencies.
- Use a virtual environment to avoid conflicts with system-wide packages.

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software in accordance with the license terms.

---

**Contact Information**

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com).

---

**Disclaimer**: This application uses OpenAI's GPT-3.5-turbo model and embedding models. Ensure compliance with OpenAI's [Terms of Use](https://openai.com/policies/terms-of-use) when using this software.
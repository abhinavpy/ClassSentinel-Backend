# main.py or a separate utils.py

from PyPDF2 import PdfReader
import docx2txt
from tika import parser
import openai
import os
import tiktoken

openai.api_key = os.getenv('OPENAI_API_KEY')






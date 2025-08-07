import os
import tempfile
import requests
import gc
from functools import lru_cache
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# ✅ Load embedding model only once
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ✅ Download PDF and save temporarily
def download_pdf(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download document.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

# ✅ Extract text from PDF
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# ✅ Create vector store from text
def get_faiss_vectorstore(text: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)  # smaller chunks = less memory
    chunks = text_splitter.split_text(text)
    return FAISS.from_texts(chunks, embeddings)

# ✅ Optional cache to reuse vectorstores (can be removed if not needed)
@lru_cache(maxsize=8)
def get_faiss_vectorstore_cached(text: str):
    return get_faiss_vectorstore(text)

# ✅ Ask question using Groq (using smaller model)
def generate_answer_with_groq(context: str, question: str) -> str:
    prompt = f"""Use the following context to answer the question:

Context:
{context}

Question:
{question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",  # smaller model = less memory
        messages=[
            {"role": "system", "content": "You are an expert document assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# ✅ Main function
def answer_questions(url: str, questions: list[str]) -> list[str]:
    pdf_path = download_pdf(url)
    text = extract_text_from_pdf(pdf_path)

    # Build or reuse vectorstore
    vectordb = get_faiss_vectorstore_cached(text)

    del text
    gc.collect()

    answers = []
    for q in questions:
        docs = vectordb.similarity_search(q, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        answer = generate_answer_with_groq(context, q)
        answers.append(answer)

        del docs, context, answer
        gc.collect()

    del vectordb
    gc.collect()

    # Cleanup temporary PDF
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return answers

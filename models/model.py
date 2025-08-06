import os
import tempfile
import requests
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq
from dotenv import load_dotenv
import gc
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# Use HuggingFace model for embeddings (Open-source, free)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def download_pdf(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download document.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def get_faiss_vectorstore(text: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return FAISS.from_texts(chunks, embeddings)

def generate_answer_with_groq(context: str, question: str) -> str:
    prompt = f"""Use the following context to answer the question:

Context:
{context}

Question:
{question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",  # or another Groq-supported model
        messages=[
            {"role": "system", "content": "You are an expert document assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def answer_questions(url: str, questions: list[str]) -> list[str]:
    print("📄 Downloading PDF from:", url)
    pdf_path = download_pdf(url)
    
    print("📑 Extracting text from:", pdf_path)
    text = extract_text_from_pdf(pdf_path)

    print("✂️ Splitting text...")
    vectordb = get_faiss_vectorstore(text)

    answers = []
    for q in questions:
        print("🤖 Question:", q)
        docs = vectordb.similarity_search(q, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        print("📚 Context length:", len(context))

        answer = generate_answer_with_groq(context, q)
        answers.append(answer)

    print("✅ All answers generated.")
    del model
    gc.collect()

    return answers


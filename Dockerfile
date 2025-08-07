# ✅ Use slim Python image to reduce image size and RAM usage
FROM python:3.10-slim

# ✅ Prevent Python from writing pyc files and enable instant output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ✅ Set working directory
WORKDIR /app

# ✅ Install required system dependencies for PDF, FAISS, and OpenBLAS
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# ✅ Upgrade pip
RUN pip install --upgrade pip

# ✅ Install PyTorch (CPU-only) and friends — stable and compatible with Python 3.10
RUN pip install torch==2.1.2+cpu torchvision==0.16.2+cpu torchaudio==2.1.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# ✅ Copy requirements and install dependencies (groq fixed at 0.2.2)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy rest of the application
COPY . .

# ✅ Expose port used by Railway
EXPOSE 10000

# ✅ Start FastAPI server with a single worker to avoid OOM issues
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port=${PORT} --workers=1"]

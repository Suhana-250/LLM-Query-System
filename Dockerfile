# ✅ Use slim base image
FROM python:3.10-slim

# ✅ Avoid bytecode files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ✅ Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# ✅ Upgrade pip
RUN pip install --upgrade pip

# ✅ Install PyTorch CPU-only (latest working versions)
RUN pip install torch==2.1.2+cpu torchvision==0.16.2+cpu torchaudio==2.1.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# ✅ Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy rest of the app
COPY . .

# ✅ Expose the port used by Railway
EXPOSE 10000

# ✅ Launch app with 1 worker to limit memory usage
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port=${PORT} --workers=1"]

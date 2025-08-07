# ✅ Use slim base image to reduce image size and memory
FROM python:3.10-slim

# ✅ Avoid writing .pyc files and enable instant logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ✅ Install only required system packages (minimal set)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy requirements and install dependencies
COPY requirements.txt ./

# ✅ Clean pip cache and install PyTorch CPU-only first
RUN pip install --upgrade pip \
 && pip install torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html \
 && pip install --no-cache-dir -r requirements.txt

# ✅ Copy the full app after dependencies are installed (Docker cache optimization)
COPY . .

# ✅ Expose port and run uvicorn with 1 worker (memory saving)
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]

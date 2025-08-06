FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu \
  -f https://download.pytorch.org/whl/cpu/torch_stable.html

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]

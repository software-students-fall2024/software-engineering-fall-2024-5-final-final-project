FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt


RUN test -f ./models/SmolLM-135M.Q2_K.gguf || \
   huggingface-cli download QuantFactory/SmolLM-135M-GGUF --include "SmolLM-135M.Q2_K.gguf" --local-dir ./models


RUN test -f ./models/Ministral-8B-Instruct-2410-Q4_K_M.gguf || \
   huggingface-cli download bartowski/Ministral-8B-Instruct-2410-GGUF --include "Ministral-8B-Instruct-2410-Q4_K_M.gguf" --local-dir ./models

COPY . .

EXPOSE 5002

CMD ["python", "app.py"]
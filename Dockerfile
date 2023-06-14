FROM debian:11

WORKDIR /app

RUN apt update && apt upgrade -y

RUN apt install pip -y

RUN pip install uvicorn fastapi

COPY ./app/main.py ./main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

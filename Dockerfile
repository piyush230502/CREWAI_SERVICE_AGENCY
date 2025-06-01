FROM python:3.10.16-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

EXPOSE 8000

CMD ["streamlit","run", "app.py"]

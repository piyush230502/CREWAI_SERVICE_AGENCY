# Deployment instructions for AI Services Agency Flask + Frontend app

## 1. Requirements
- Python 3.10+
- pip
- (Recommended) Virtual environment
- Gunicorn (for production WSGI server)
- Nginx (for reverse proxy, static file serving)

## 2. Install dependencies

```
pip install -r requirements.txt
gunicorn
```

## 3. Environment variables
- Set your Groq API key as an environment variable or provide it via the frontend form.
- (Optional) Use a `.env` file and `python-dotenv` for local development.

## 4. Gunicorn (WSGI) launch (production)

```
gunicorn app:app --bind 0.0.0.0:8000 --workers 4
```

- The app will be available at `http://localhost:8000`.

## 5. Nginx configuration (recommended)

Example `/etc/nginx/sites-available/crewai_agency`:

```
server {
    listen 80;
    server_name your_domain.com;

    root /path/to/CREWAI_SERVICE_AGENCY/frontend;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/CREWAI_SERVICE_AGENCY/frontend/;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- Reload nginx: `sudo systemctl reload nginx`

## 6. Folder structure

```
CREWAI_SERVICE_AGENCY/
├── app.py
├── crewai_app.py
├── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── ...
```

## 7. (Optional) Docker deployment

Create a `Dockerfile`:

```
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn
EXPOSE 8000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

Build and run:
```
docker build -t crewai-agency .
docker run -d -p 8000:8000 crewai-agency
```

## 8. Security & Notes
- Never commit your API keys.
- Use HTTPS in production (Let’s Encrypt + Nginx).
- For scaling, use a process manager (systemd, supervisor, etc.) for Gunicorn.

---

For questions or issues, see the README or contact the maintainer.

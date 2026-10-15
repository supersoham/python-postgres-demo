
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create a dedicated, unprivileged application user.
RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app app

# Install dependencies while building the image.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application with ownership assigned to the app user.
COPY --chown=app:app app.py .

USER app

EXPOSE 5000

CMD ["python", "app.py"]
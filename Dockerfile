FROM python:3.9-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages from the backend folder
COPY backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code from the backend/app folder
COPY backend/app /code/app

# Set environment variables for FastAPI
ENV PORT=7860

# Expose the default port Hugging Face maps
EXPOSE 7860

# Start Uvicorn pointing to the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]

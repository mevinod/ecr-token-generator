# Use an official lightweight Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app.py .

# Expose Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]

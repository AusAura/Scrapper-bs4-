# Using base Python
FROM python:3.11

# Setting working directory
WORKDIR /app

# Copy app files to container
COPY . .

# Setting env variable for Python
ENV PYTHONPATH=/app

# Installing dependencies
RUN pip install -r requirements.txt

# Exposing port
EXPOSE 8005

# Starting scripts
CMD ["python", "src/models.py"]
CMD ["python", "src/autobackup.py"]
CMD ["python", "src/autoparse.py"]
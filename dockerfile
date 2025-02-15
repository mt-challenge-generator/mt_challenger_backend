# Use the official Python image from the Docker Hub
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev-compat \
    libmariadb-dev \
    && apt-get clean

# Install virtualenv
RUN pip install virtualenv

# Create a virtual environment
RUN virtualenv venv

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies in the virtual environment
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

# Copy the project files
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the application using Django's development server
CMD ["venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
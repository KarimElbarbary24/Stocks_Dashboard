# syntax=docker/dockerfile:1

# Use an official Python image as a base
FROM python:3.12.5-slim

# Set the working directory
WORKDIR /Stocks_Dashboard

# Copy and install requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8050

# Define the default command
CMD ["python", "app.py"]

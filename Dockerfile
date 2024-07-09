# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the app files into the container
COPY *.py ./
COPY barcode_images/ ./barcode_images/
COPY submission_templates/ ./submission_templates/
COPY helper_functions/ ./helper_functions/
# Make port ${PORT} available to the world outside this container
EXPOSE ${PORT}

# Run the app when the container launches
CMD sh -c "streamlit run colony_picking_app.py \
  --server.headless true \
  --server.fileWatcherType none \
  --browser.gatherUsageStats false \
  --server.port=${PORT} \
  --server.address=0.0.0.0"


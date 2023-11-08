# Use the official Python image as the base image
FROM python:3.7

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container
COPY . .

# Install project dependencies
RUN apt update && apt install -y chromium
RUN pip install .

# Run the ookiebot using the Python interpreter
CMD ["python3.7", "-m", "ookiebot", "https://reddit.com", "https://4chan.org"]
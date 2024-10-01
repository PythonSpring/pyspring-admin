# Use a Python 3.10+ base image
FROM python:3.12

WORKDIR /app

RUN apt update && apt install git -y

COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Copy the project files into the container
COPY . /app

# Expose the necessary port (modify this if your app runs on a different port)
EXPOSE 8080

# Command to run the application (adjust this based on your entry point)
CMD ["python", "./main.py"]
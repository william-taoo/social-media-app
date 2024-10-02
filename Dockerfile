# Use an official Python runtime as a parent image
FROM python:latest

# Define environment variable
ENV FLASK_APP=main.py
ENV APP_HOME=/app
# Set the working directory in the container
WORKDIR $APP_HOME

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Run flask app when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
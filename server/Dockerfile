# Use an official Python runtime as a parent image,
# need to use 3.7 as 3.7-slim breaks the GCC compile of sanic
FROM python:3.7

# Set the working directory to /py_chator
WORKDIR /ssh_blocker

# Copy the current directory contents into the container at /py_chator
ADD . /ssh_blocker

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
# EXPOSE 80
# Commented out as docker-compose does this now

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "server.py"]

# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Flit
RUN pip install flit

# Use Flit to install the package and its dependencies
RUN flit install

# Command to run the app
# CMD ["python", "app.py"]

# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Flit
RUN pip install flit

# Use Flit to install the package and its dependencies
ENV FLIT_ROOT_INSTALL=1
RUN flit install

# Create a new user and group
RUN groupadd -r usergroup && useradd -r -g usergroup meow

# Switch to the new user
USER meow

# Command to run the app
# CMD ["python", "app.py"]

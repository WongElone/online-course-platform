# Use the official Python base image with version 3.7
FROM python:3.8

# Copy the project files to the container
COPY online_course_platform /app

# Set the working directory inside the container
WORKDIR /app

ENV DJANGO_ENV=prod

# Install the project dependencies
# Set the command to run the Django development server
CMD pip3 install --upgrade pip; pip3 install --no-cache-dir -r requirements.txt; pip3 install python-dotenv; python manage.py runserver 0.0.0.0:8000

# Expose the port that the Django app will run on
EXPOSE 8000

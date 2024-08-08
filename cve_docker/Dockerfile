# Use the official AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Copy the function code
COPY app.py /var/task
COPY requirements.txt /var/task

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /var/task/requirements.txt


# Set the CMD to your handler (format: file.function)
CMD [ "app.lambda_handler" ]




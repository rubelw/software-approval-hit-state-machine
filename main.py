#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil
from configparser import ConfigParser
import zipfile

def zip_single_file(file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, arcname=file_path.split('/')[-1])


def run_terraform_command(command):
    """
    Run a Terraform command.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error: {stderr.decode('utf-8')}")
        raise Exception(f"Command '{command}' failed")

    print(stdout.decode('utf-8'))


def check_aws_credentials():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if aws_access_key_id and aws_secret_access_key:
        return True
    else:
        return False

def set_aws_environment_variables():
    # Path to the AWS credentials file
    credentials_file_path = os.path.expanduser("~/.aws/credentials")

    # Read the credentials file
    config = ConfigParser()
    config.read(credentials_file_path)

    # Get the access key ID and secret access key for the default profile
    aws_access_key_id = config.get("default", "aws_access_key_id", fallback=None)
    aws_secret_access_key = config.get("default", "aws_secret_access_key", fallback=None)

    if aws_access_key_id and aws_secret_access_key:
        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

def get_aws_region():
    # Path to the AWS configuration file
    config_file_path = os.path.expanduser("~/.aws/config")

    # Read the configuration file
    config = ConfigParser()
    config.read(config_file_path)

    # Get the region for the default profile
    aws_region = config.get("default", "region", fallback=None)

    if aws_region:
        return aws_region

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created successfully")
    except OSError as error:
        print(f"Error creating directory '{path}': {error}")

def get_current_working_directory():
    try:
        cwd = os.getcwd()
        print(f"Current working directory: {cwd}")
        return cwd
    except Exception as e:
        print(f"Error getting current working directory: {e}")
        return None

def install_requests(package_dir):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests","-t", package_dir+'/'])
        print("Requests installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requests: {e}")

def copy_file_to_directory(source_file, destination_directory):
    try:
        # Ensure the destination directory exists
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)
            print(f"Created destination directory: {destination_directory}")

        # Copy the file to the destination directory
        shutil.copy2(source_file, destination_directory)
        print(f"Copied '{source_file}' to '{destination_directory}' successfully")
    except Exception as e:
        print(f"Error copying file '{source_file}' to '{destination_directory}': {e}")


def create_lambda_package(lambda_code_file,package_dir,zip_file):
    # Define paths

    # Create a directory for dependencies
    if not os.path.exists(package_dir):
        os.makedirs(package_dir)

    # Install dependencies
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'urllib3==1.26.14', '-t', package_dir])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', '-t', package_dir])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mysql-connector-python', '-t', package_dir])



    # Copy the Lambda function code into the directory
    shutil.copy(lambda_code_file, package_dir)

    # Create the zip file
    shutil.make_archive(base_name=zip_file.replace('.zip', ''), format='zip', root_dir=package_dir)

    # Clean up the package directory
    shutil.rmtree(package_dir)

    print(f"Created Lambda package: {zip_file}")


def create_numpy_package(zip_file):
    # Define paths

    # Create a directory for dependencies
    if not os.path.exists('numpy_package'):
        os.makedirs('numpy_package')

    # Install dependencies
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas', '-t', 'numpy_package'])

    # Create the zip file
    shutil.make_archive(base_name=zip_file.replace('.zip', ''), format='zip', root_dir='numpy_package')

    # Clean up the package directory
    shutil.rmtree('numpy_package')

    print(f"Created Lambda package: {zip_file}")


def run_bash_command(command):
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Decode the output and error messages
        output = result.stdout.decode('utf-8')
        error = result.stderr.decode('utf-8')

        # Print the output and error messages
        print("Output:\n", output)
        print("Error:\n", error)

        return result.returncode

    except subprocess.CalledProcessError as e:
        # Handle errors in the command execution
        print(f"Command '{command}' failed with return code {e.returncode}")
        print(f"Error output: {e.stderr.decode('utf-8')}")
        return e.returncode


def change_directory(path):
    try:
        # Change the current working directory
        os.chdir(path)
        print(f"Successfully changed directory to: {os.getcwd()}")
    except FileNotFoundError:
        print(f"Error: The directory {path} does not exist.")
    except NotADirectoryError:
        print(f"Error: {path} is not a directory.")
    except PermissionError:
        print(f"Error: Permission denied to change to {path}.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main(arguments):

    print('arguments: '+str(arguments))
    # Change to the directory containing the Terraform configuration
    mycwd = get_current_working_directory()
    print(str(mycwd))

    # Build the Docker image
    change_directory(mycwd+'/software_docker')
    run_bash_command('docker build -t my_custom_image:latest .')


    change_directory(mycwd+'/cve_docker')
    run_bash_command('docker build -t my_custom_cve_image:latest .')

    change_directory(mycwd)

    if arguments and len(arguments) > 1:
        print('destroying terraform')
        terraform_directory = mycwd + "/tf"
        os.chdir(terraform_directory)

        # Initialize Terraform
        run_terraform_command("terraform destroy -auto-approve")

    else:

        # Example usage
        region = get_aws_region()
        set_aws_environment_variables()
        check_aws_credentials()
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        print("export AWS_ACCESS_KEY_ID="+str(aws_access_key_id))
        print("export AWS_SECRET_ACCESS_KEY="+str(aws_secret_access_key))
        print("export AWS_DEFAULT_REGION="+str(region))

        create_lambda_package(mycwd+'/tf/lambda_function_5.py','lambda_package5',mycwd+'/tf/lambda_function_5_payload.zip')
        create_lambda_package(mycwd+'/tf/lambda_function_6.py','lambda_package6',mycwd+'/tf/lambda_function_6_payload.zip')

        terraform_directory = mycwd+"/tf"
        os.chdir(terraform_directory)

        # Initialize Terraform
        run_terraform_command("terraform init")


        # Apply the Terraform configuration
        run_terraform_command("terraform apply -auto-approve")


if __name__ == "__main__":
    arguments = sys.argv

    # This block will only be executed if the script is run directly, not if it's imported as a module
    main(arguments)

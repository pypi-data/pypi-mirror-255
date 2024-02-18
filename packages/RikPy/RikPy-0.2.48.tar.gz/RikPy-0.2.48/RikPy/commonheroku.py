from dotenv import load_dotenv
import requests
import os
import uuid 
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from urllib.parse import urlparse
from datetime import datetime
from .commonfunctions import download_file_local, delete_local_file
from .commonlogging import configure_logger

logger = configure_logger()

def heroku_environment():
    load_dotenv()  # This loads the environment variables from .env
    CLOUDCUBE_ACCESS_KEY_ID = os.getenv("CLOUDCUBE_ACCESS_KEY_ID")
    CLOUDCUBE_SECRET_ACCESS_KEY = os.getenv("CLOUDCUBE_SECRET_ACCESS_KEY")
    CLOUDCUBE_URL = os.getenv("CLOUDCUBE_URL")
    HEROKU_API_KEY  = os.getenv("HK_API_KEY")
    HEROKU_APP_NAME = os.getenv("HK_APP_NAME")

    # Extract the bucket name from the CLOUDCUBE_URL
    cube_name = CLOUDCUBE_URL.split('/')[-1]
    cube_public = f"{cube_name}/public/"
    bucket_name = CLOUDCUBE_URL.split('.')[0].split('//')[1]

    # Create a dictionary to store the values
    heroku_config_dict = {
        "CLOUDCUBE_ACCESS_KEY_ID": CLOUDCUBE_ACCESS_KEY_ID,
        "CLOUDCUBE_SECRET_ACCESS_KEY": CLOUDCUBE_SECRET_ACCESS_KEY,
        "CLOUDCUBE_URL": CLOUDCUBE_URL,
        "HEROKU_API_KEY": HEROKU_API_KEY,
        "HEROKU_APP_NAME": HEROKU_APP_NAME,
        "CUBE_NAME": cube_name,
        "CUBE_PUBLIC": cube_public,
        "BUCKET_NAME": bucket_name
    }

    return heroku_config_dict

def heroku_upload_file(file_name, folder=None, heroku_config_dict=None):

    # Ensure folder ends with a '/' if it's not empty
    if folder is None:
        folder = ''
    elif not folder.endswith('/'):
        folder += '/'

    if heroku_config_dict is None:
        raise ValueError("heroku_config_dict is required for this function.")
    
    # Extract relevant values from heroku_config_dict
    CLOUDCUBE_ACCESS_KEY_ID = heroku_config_dict.get("CLOUDCUBE_ACCESS_KEY_ID")
    CLOUDCUBE_SECRET_ACCESS_KEY = heroku_config_dict.get("CLOUDCUBE_SECRET_ACCESS_KEY")
    CLOUDCUBE_URL = heroku_config_dict.get("CLOUDCUBE_URL")
    CUBE_PUBLIC = heroku_config_dict.get("CUBE_PUBLIC")
    BUCKET_NAME = heroku_config_dict.get("BUCKET_NAME")

    # Construct the full S3 object name
    object_name = CUBE_PUBLIC + folder + file_name

    try:
        # Create an S3 client with CloudCube credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=CLOUDCUBE_ACCESS_KEY_ID,
            aws_secret_access_key=CLOUDCUBE_SECRET_ACCESS_KEY
        )

        # Upload the file
        s3_client.upload_file(file_name, BUCKET_NAME, object_name)

         # Split the object_name by '/'
        parts = object_name.split('/')

        # Exclude the first part (wwmx700brb7g) and join the rest with CLOUDCUBE_URL
        full_url = f"{CLOUDCUBE_URL}/{'/'.join(parts[1:])}"
        
        return full_url
    
    except FileNotFoundError:
        return "The file was not found."
    except NoCredentialsError:
        return "Credentials not available."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def heroku_upload_file_from_url(file_url, folder, heroku_config_dict=None, bnewname=False):
    
    # Download the file to a local path
    file_path = download_file_local(file_url)

    if bnewname:
        # Extract the file extension from the URL
        parsed_url = urlparse(file_url)
        file_extension = os.path.splitext(os.path.basename(parsed_url.path))[1]

        # Generate a timestamp in the format YYYYMMDDHHMMSS
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Generate a UUID
        generated_uuid = uuid.uuid4()

        # Convert the UUID to a hexadecimal string and truncate it to the desired length
        shortened_uuid = str(generated_uuid.hex)[:8]  # Example: Truncate to 8 characters

        # Create a new filename using the shortened UUID
        new_filename = f"{timestamp}_{shortened_uuid}{file_extension}"

        # Rename the local file with the new filename
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        os.rename(file_path, new_file_path)

        # Upload the file with the new filename
        object_name = heroku_upload_file(new_file_path, folder, heroku_config_dict)

        # Delete the local file (both the original and renamed versions)
        delete_local_file(new_file_path)
    else:
        # Upload the file with its original name
        object_name = heroku_upload_file(file_path, folder, heroku_config_dict)

        # Delete the local file
        delete_local_file(file_path)

    return object_name

def heroku_list_files_in_folder(folder_name, heroku_config_dict=None):
    try:
        if heroku_config_dict is None:
            raise ValueError("heroku_config_dict is required for this function.")

        # Extract relevant values from heroku_config_dict
        CLOUDCUBE_ACCESS_KEY_ID = heroku_config_dict.get("CLOUDCUBE_ACCESS_KEY_ID")
        CLOUDCUBE_SECRET_ACCESS_KEY = heroku_config_dict.get("CLOUDCUBE_SECRET_ACCESS_KEY")
        CUBE_PUBLIC = heroku_config_dict.get("CUBE_PUBLIC")
        BUCKET_NAME = heroku_config_dict.get("BUCKET_NAME")

        # Create an S3 client with CloudCube credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=CLOUDCUBE_ACCESS_KEY_ID,
            aws_secret_access_key=CLOUDCUBE_SECRET_ACCESS_KEY
        )

        # Set the prefix based on folder_name
        full_prefix = CUBE_PUBLIC
        full_prefix = ""
        print(full_prefix)
        if folder_name:
            if not folder_name.endswith('/'):
                folder_name += '/'
            full_prefix += folder_name
        print(full_prefix)

        # List objects in the specified folder
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=full_prefix)
        print(f"response: {response}")
        # Check if the bucket has contents
        if 'Contents' in response:
            print("Contents")
            files = [item['Key'] for item in response['Contents']]
            return files
        else:
            return []
    except ValueError as ve:
        logger.error(f"An error occurred: {ve}")
        return f"ValueError: {str(ve)}"
    except NoCredentialsError:
        logger.error("Credentials not available.")
        return []
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []

def heroku_delete_file(file_key, heroku_config_dict=None):
    try:
        if heroku_config_dict is None:
            raise ValueError("heroku_config_dict is required for this function.")

        # Extract relevant values from heroku_config_dict
        CLOUDCUBE_ACCESS_KEY_ID = heroku_config_dict.get("CLOUDCUBE_ACCESS_KEY_ID")
        CLOUDCUBE_SECRET_ACCESS_KEY = heroku_config_dict.get("CLOUDCUBE_SECRET_ACCESS_KEY")
        BUCKET_NAME = heroku_config_dict.get("BUCKET_NAME")

        # Create an S3 client with CloudCube credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=CLOUDCUBE_ACCESS_KEY_ID,
            aws_secret_access_key=CLOUDCUBE_SECRET_ACCESS_KEY
        )

        # Delete the file
        response = s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)
        return f"File {file_key} successfully deleted from bucket {BUCKET_NAME}."
    
    except ValueError as ve:
        logger.error(f"An error occurred: {ve}")
        return []
    except NoCredentialsError:
        logger.error("Credentials not available")
        return []
    except ClientError as e:
        logger.error(f"An error occurred: {e}")
        return []
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []
    
def heroku_download_files_in_folder(folder_name, heroku_config_dict=None, bdelete=False):

    user_home = os.path.expanduser("~")
    local_download_folder = os.path.join(user_home, 'Downloads', folder_name)

    CLOUDCUBE_ACCESS_KEY_ID = heroku_config_dict.get("CLOUDCUBE_ACCESS_KEY_ID")
    CLOUDCUBE_SECRET_ACCESS_KEY = heroku_config_dict.get("CLOUDCUBE_SECRET_ACCESS_KEY")
    cube_public = heroku_config_dict.get("CUBE_PUBLIC")
    bucket_name = heroku_config_dict.get("BUCKET_NAME")

    # Create an S3 client with CloudCube credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=CLOUDCUBE_ACCESS_KEY_ID,
        aws_secret_access_key=CLOUDCUBE_SECRET_ACCESS_KEY
    )

    # Set the prefix based on folder_name
    full_prefix = cube_public
    if folder_name:
        if not folder_name.endswith('/'):
            folder_name += '/'
        full_prefix += folder_name

    try:

        # List objects in the specified folder
        objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=full_prefix)['Contents']
        
        # Ensure the local_download_folder exists
        print(local_download_folder)
        os.makedirs(local_download_folder, exist_ok=True)

        # Download files to the local subfolder
        for obj in objects:
            file_key = obj['Key']
            local_file_path = os.path.join(local_download_folder, os.path.basename(file_key))
            response=s3_client.download_file(bucket_name, file_key, local_file_path)

            # If bdelete is True, delete the file from the S3 bucket
            if bdelete:
                print("Deleting file:")
                print("Bucket Name:", bucket_name)
                print("File Key:", file_key)
                try:
                    heroku_delete_file(file_key=file_key, heroku_config_dict=heroku_config_dict)
                    #s3_client.delete_object(Bucket=bucket_name, Key=file_key)
                    #print(f"Deleted file {file_key} from bucket {bucket_name}.")
                except ClientError as e:
                    print(f"Error deleting file {file_key}: {e}")

        return len(objects)
    
    except NoCredentialsError:
        print("Credentials not available.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
    
def get_heroku_credentials(heroku_config_dict=None):
    try:
        if heroku_config_dict is None:
            raise ValueError("heroku_config_dict is required for this function.")

        HEROKU_API_KEY = heroku_config_dict.get("HEROKU_API_KEY")
        HEROKU_APP_NAME = heroku_config_dict.get("HEROKU_APP_NAME")

        # Heroku API endpoint to get config vars
        url = f"https://api.heroku.com/apps/{HEROKU_APP_NAME}/config-vars"

        # Headers for Heroku API authentication
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {HEROKU_API_KEY}"
        }

        # Making the request to Heroku API
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            config_vars = response.json()
            # Assuming DATABASE_URL is the key for your database credentials
            db_url = config_vars.get('DATABASE_URL')
            if db_url:
                return parse_database_url(db_url)
            else:
                logger.error("Database URL not found in config vars")
                print("Database URL not found in config vars")
                return "Database URL not found in config vars"
 
        else:
            logger.error(f"Failed to retrieve config vars from Heroku. Status Code: {response.status_code}")
            print("Failed to retrieve config vars from Heroku. Status Code:", response.status_code)
            return f"Failed to retrieve config vars from Heroku. Status Code: {response.status_code}"
    
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        print(f"ValueError: {str(ve)}")
        return f"ValueError: {str(ve)}"
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")
        return f"An unexpected error occurred: {str(e)}"

def parse_database_url(db_url):
    """ Parse the database URL into its components """
    parsed_url = urlparse(db_url)
    username = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port
    database = parsed_url.path[1:]  # Remove the leading '/'

    return {
        "username": username,
        "password": password,
        "host": host,
        "port": port,
        "database": database
    }
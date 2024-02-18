from .commonheroku import heroku_environment, heroku_upload_file_from_url, heroku_list_files_in_folder, heroku_download_files_in_folder, heroku_delete_file
from .commonshopify import Shopify_get_products_in_collection, Shopify_get_metaobject_gid, Shopify_update_metaobject, Shopify_get_collections
from .commons3 import s3_download_files_in_folder, s3_list_files_in_folder, s3_environment, s3_upload_file_from_url, s3_upload_local_file, s3_delete_file
import json
import boto3
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import requests
from .commonfunctions import download_file_local, send_email
from .commonopenai import OpenAI_generate_image, OpenAI_generate_response

b_test_heroku = False
b_test_shopify = False
b_test_s3 = False
b_test_openai = True
b_test_email = False

if b_test_email:
    email_type="Info"
    email_message="Mensaje de prueba"
    originator="RikPy"
    send_email(email_type=email_type, email_message=email_message, originator=originator)

if b_test_shopify:
    ########## Test shopify multibanner load
    shop = '9d9853'
    access_token = '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'
    metaobject_type = 'product_banner'
    metaobject_handle = 'vinzo-3-product-banner'

    # image1_url="https://getaiir.s3.eu-central-1.amazonaws.com/wine/20240129215403_1dc3765c.png"
    # image2_url="https://getaiir.s3.eu-central-1.amazonaws.com/wine/20240129215346_a08a387b.png"
    # image2_url="https://getaiir.s3.eu-central-1.amazonaws.com/wine/20240129212907_38873eb0.png"

    # Load banners to Shopify
    # banner_url = image1_url
    # mobile_banner_url = image1_url
    # metaobject_banner_number = 2
    # product_url="https://vinzo.uk/products/emilio-moro-vendimia-seleccionada-2021"
    # metaobject_gid = Shopify_get_metaobject_gid(shop=shop, access_token=access_token, metaobject_type=metaobject_type, handle=metaobject_handle)
    # Shopify_update_metaobject(shop=shop, access_token=access_token, metaobject_gid=metaobject_gid, banner_url=banner_url, mobile_banner_url=mobile_banner_url, product_url=product_url, metaobject_banner_number=metaobject_banner_number)

    collections = Shopify_get_collections(shop, access_token)
    print(collections)

    collection_id = '450597257527'
    #products = Shopify_get_products_in_collection(shop, access_token, '450597257527')
    #print(products)

if b_test_s3:

    S3_ACCESS_KEY_ID = 'AKIAVRUVVBONIFTN4GAX'
    S3_SECRET_ACCESS_KEY = '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'
    S3_URL = 'https://getaiir.s3.eu-central-1.amazonaws.com'
    S3_CUBE_PUBLIC = 'getaiir/public/'
    S3_BUCKET_NAME = 'getaiir'
    S3_CUBE_NAME = 'eu-central-1'

    s3_config_dict = {
        "S3_ACCESS_KEY_ID": S3_ACCESS_KEY_ID,
        "S3_SECRET_ACCESS_KEY": S3_SECRET_ACCESS_KEY,
        "S3_URL": S3_URL,
        "S3_CUBE_NAME": S3_CUBE_NAME,
        "S3_CUBE_PUBLIC": S3_CUBE_PUBLIC,
        "S3_BUCKET_NAME": S3_BUCKET_NAME
    }

    #################################

    s3_list_files_in_folder(folder_name="wine/image", s3_config_dict=s3_config_dict)

    dest_folder="c:\\users\\rforn\\downloads\\wine"
    dest_folder="C:\\Users\\rforn\\Dropbox\\My PC (LAPTOP-7IFP1HKP)\\Downloads\\BorrarWine"
    dest_folder="C:\\Users\\rforn\\Dropbox\\Code\\RikPy\\Downloads\\Wine"
    folder_name="wine/image"
    s3_download_files_in_folder(folder_name=folder_name, destination_folder=dest_folder, s3_config_dict=s3_config_dict)

    exit()

    url="https://files.canvas.switchboard.ai/4ea249ec-1808-4a19-afd7-0a251a8d8aaf/1aaced80-f587-41a2-855c-33501840f337.png"
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    print(local_filename)

    mobile_banner_image = url

    profile_topic = "wine"

    bnewname = True
    mobile_banner_url = s3_upload_file_from_url(file_url=mobile_banner_image, folder_name=profile_topic, s3_config_dict=s3_config_dict, bnewname=bnewname)        
    print(mobile_banner_url)

    print

    
    #####################

    # s3_config_dict = s3_environment()

    print(s3_config_dict)
    
    objects = s3_list_files_in_folder(folder_name="public", s3_config_dict=s3_config_dict)

    exit()

    file_url="https://cloud-cube-eu2.s3.amazonaws.com/wwmx700brb7g/public/dogs/16264433-d3aa-4dbd-8318-722bde7ca2bb.png"
    local_file_path = '.gitignore'
    folder_name="public/wine"
    response=s3_upload_local_file(file_name=local_file_path, folder_name=folder_name, s3_config_dict=s3_config_dict)
    print(response)
    object_key=folder_name+"/"+local_file_path
    s3_delete_file(object_key=object_key, s3_config_dict=s3_config_dict)

    object_key = s3_upload_file_from_url(file_url=file_url, folder_name=folder_name, s3_config_dict=s3_config_dict, bnewname=True, make_public=False)
    print(object_key)

if b_test_heroku:

    heroku_config_dict = heroku_environment()
    folder="wine"
    files=heroku_list_files_in_folder(folder_name=folder, heroku_config_dict=heroku_config_dict)

    # heroku_download_files_in_folder(folder_name=folder, heroku_config_dict=heroku_config_dict, bdelete=True)
    # response = heroku_delete_file(file_key=file_key, heroku_config_dict=heroku_config_dict)
    # print(response)

if b_test_openai:
    load_dotenv()  # This loads the environment variables from .env
    openai_key = os.getenv("OPEN_AI_KEY")
    prompt="Tell me a joke"
    response = OpenAI_generate_response(prompt=prompt, openai_key=openai_key)
    print(response)
    print(response.data)
    print(response.status_code)
    if response.status_code != 200:
        print(f"Error occurred: {response.data}")
        exit()
    # post_details = json.loads(response.choices[0].message.content.strip())
    message_content = response.data.choices[0].message.content

    print(message_content)

    image_prompt = "An image of a gorila in a surreal jungle with melting timeclocks"
    response = OpenAI_generate_image(image_prompt=image_prompt, number_images=1, size="1024x1792", openai_key=openai_key)
    print(response)
    print(response.data)
    print(response.status_code)
    if response.status_code != 200:
        print(f"Error occurred: {response.data}")
        exit()
    
    image_response = response.data
    image_url = image_response.data[0].url
    print(image_url)
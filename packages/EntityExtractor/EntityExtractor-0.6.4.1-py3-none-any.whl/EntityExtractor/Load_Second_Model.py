import threading
import re
import nltk 
from bs4 import BeautifulSoup 
from nltk.corpus import stopwords
import spacy
from collections import defaultdict
import base64
import os
from spacy.tokens import DocBin # for serialization
import requests
import zipfile
import logging

class LoadSecondModel:

    __EMAIL_PARSER_MODEL_ZIP_URL = 'https://d2olrrfwjazc7n.cloudfront.net/website/assets/entity_extraction_model/output/output_SECOND.zip'
    __BASE_DIR = os.getcwd()
    __local_zip_file_path = os.path.join(__BASE_DIR, 'output_SECOND.zip')
    __extract_to = __BASE_DIR
    __modelInstance = None
    __lock = threading.Lock()
    
    @classmethod
    def __get_modal_instance(cls):
        with cls.__lock:
            if cls.__modelInstance is None:
                cls.__modelInstance = cls.__load_model()

            return cls.__modelInstance


    
    @classmethod
    def __load_model(cls):
        try:
            logging.info("Checking Second Model File")
            if os.path.exists(cls.__local_zip_file_path) and os.path.exists(os.path.join(cls.__extract_to, 'output_SECOND//model-best')):
                logging.info("Loading Pretrained Second Model")
                nlp = spacy.load(os.path.join(cls.__extract_to, 'output_SECOND//model-best'))
                logging.info("Model Second has been loaded")
                return nlp
            
            elif os.path.exists(cls.__local_zip_file_path):
                logging.info("Unzipping File to: %s", cls.__extract_to)
                with zipfile.ZipFile(cls.__local_zip_file_path, 'r') as zip_ref:
                            os.makedirs(cls.__extract_to, exist_ok=True)
                            zip_ref.extractall(cls.__extract_to)
                            logging.info("Zip file extracted to %s", cls.__extract_to)

                nlp = spacy.load(os.path.join(cls.__extract_to, 'output_SECOND//model-best'))

                logging.info("Model Second has been loaded")
                return nlp

            else:
                try:
                    logging.info("Downloading Second Model File")
                    response = requests.get(cls.__EMAIL_PARSER_MODEL_ZIP_URL)

                    if response.status_code == 200:
                        logging.info("Response Code: %s", response.status_code)

                        with open(cls.__local_zip_file_path, 'wb') as file:
                            file.write(response.content)

                        logging.info("File downloaded to %s", cls.__local_zip_file_path)
                        logging.info("Unzipping File to: %s", cls.__extract_to)

                        with zipfile.ZipFile(cls.__local_zip_file_path, 'r') as zip_ref:
                            os.makedirs(cls.__extract_to, exist_ok=True)
                            zip_ref.extractall(cls.__extract_to)
                            logging.info("Zip file extracted to %s", cls.__extract_to)

                        nlp = spacy.load(os.path.join(cls.__extract_to, 'output_SECOND//model-best'))

                        logging.info("Model Second has been loaded")
                        return nlp
                    else:
                        logging.error("Failed to download the Second Model file")
                        return None
                except Exception as e:
                    logging.error("Error %s", e)
                    return None
        except Exception as e:
            logging.error("Error %s", e)
            return None
    
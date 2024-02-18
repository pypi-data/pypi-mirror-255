import threading
import pandas as pd
import numpy as np
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

logging.basicConfig(level=logging.INFO) 


class NLPOBJ:
    _instance = None
    
    def __new__(cls,*args,**kwargs):
        if NLPOBJ._instance is None:
            
            # download packages 
            nltk.download("stopwords")
            nltk.download("punkt")
            spacy.cli.download("en_core_web_trf")
            
            NLPOBJ._instance = spacy.load("en_core_web_trf")
        return NLPOBJ._instance


class LoadModel:

    __EMAIL_PARSER_MODEL_ZIP_URL = 'https://d2olrrfwjazc7n.cloudfront.net/website/assets/entity_extraction_model/output/output_FIRST.zip'
    __BASE_DIR = os.getcwd()
    __local_zip_file_path = os.path.join(__BASE_DIR, 'output.zip')
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
            logging.info("Checking Model File")
            if os.path.exists(cls.__local_zip_file_path) and os.path.exists(os.path.join(cls.__extract_to, 'output_FIRST//model-best')):
                logging.info("Loading Pretrained Model")
                nlp = spacy.load(os.path.join(cls.__extract_to, 'output_FIRST//model-best'))
                logging.info("Model has been loaded")
                return nlp
            
            elif os.path.exists(cls.__local_zip_file_path):
                logging.info("Unzipping File to: %s", cls.__extract_to)
                with zipfile.ZipFile(cls.__local_zip_file_path, 'r') as zip_ref:
                            os.makedirs(cls.__extract_to, exist_ok=True)
                            zip_ref.extractall(cls.__extract_to)
                            logging.info("Zip file extracted to %s", cls.__extract_to)

                nlp = spacy.load(os.path.join(cls.__extract_to, 'output_FIRST//model-best'))

                logging.info("Model has been loaded")
                return nlp

            else:
                try:
                    logging.info("Downloading Model File")
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

                        nlp = spacy.load(os.path.join(cls.__extract_to, 'output_FIRST//model-best'))

                        logging.info("Model has been loaded")
                        return nlp
                    else:
                        logging.error("Failed to download the file")
                        return None
                except Exception as e:
                    logging.error("Error %s", e)
                    return None
        except Exception as e:
            logging.error("Error %s", e)
            return None
    
    # def __remove_html_tags(self, text):
    #     """Function to remove HTML tags"""
    #     try:
    #         soup = BeautifulSoup(text, "html.parser")
    #         cleaned_text = soup.get_text()
    #         return cleaned_text
    #     except Exception as e:
    #         logging.error("Error removing HTML tags: %s", e)
    #         return text


    # def __clean_email(self, text):
    #     """Function to clean email text"""
        
                
    #     try:
    #         nlp = NLPOBJ()
    #         punct = set('!"#$%&\'()*+,:;<=>?@[\\]^_`{|}~_')
    #         text = re.sub(r'm[./|]v', 'mv', text.lower())
    #         text = self.__remove_html_tags(text)

    #         doc = nlp(text)

    #         text_list = [token.lower_ for token in doc if not (
    #             token.like_url or
    #             token.is_currency or
    #             token.is_space or
    #             token.text in punct or 
    #             re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", token.lower_)
    #         )]
    #         text = " ".join(text_list)
    #         return text
    #     except Exception as e:
    #         logging.error("Error %s", e)
        
        

    def __clean_email(self, text):
        """Function to clean email text"""

        try:
            nlp = NLPOBJ()
            punct = set('!"#$%&\'()*+,:;<=>?@[\\]^_`{|}~_')
            text = re.sub(r'm[./|]v', 'mv', text.lower())
            # text = self.__remove_html_tags(text)

            # Remove content after "disclaimer"
            text = re.sub(r'disclaimer.*$', '', text, flags=re.IGNORECASE)

            doc = nlp(text)

            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            text_list = [token.lower_ for token in doc if not (
                token.like_url or
                token.is_currency or
                token.is_space or
                token.text in punct or 
                re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", token.lower_) or
                token.lower_ in stop_words
            )]
            text = " ".join(text_list)
            return text
        except Exception as e:
            logging.error("Error %s", e)

             

    
    # def clean_email(text):
    #     """Clean email text by extracting relevant parts and removing unnecessary elements.
        
    #     Args:
    #         text (str): The input email text to be cleaned.
            
    #     Returns:
    #         tuple or None: If 'mv' is found in the text, returns a tuple containing two parts
    #                     (first_part, second_part). Otherwise, returns None.
    #     """
    #     try:
    #         if not isinstance(text, str):
    #             raise ValueError("Input text must be a string.")
            
    #         text = text.lower()
    #         # Replace 'm[./]v' with 'mv'
    #         text = re.sub(r'm[./]v', 'mv', text)

    #         # Check for 'mv' in text
    #         if 'mv' in text:
    #             # Extract content before 'disclaimer'
    #             content_before_disclaimer = re.search(r'(.+?)\bdisclaimer\b', text, re.DOTALL)
    #             if content_before_disclaimer:
    #                 text = content_before_disclaimer.group(1).strip()
    #             else:
    #                 # Use BeautifulSoup to extract text from HTML
    #                 soup = BeautifulSoup(text, "html.parser")
    #                 text = soup.get_text()
    #             # Remove URLs
    #             text = re.sub(r'http\S+|www.\S+', '', text) 
                
    #             # Replace specific patterns with space
    #             text = re.sub(r'\r\n|\ufeff|[-_]{2,}', ' ', text)
                
    #             # Replace multiple spaces with a single space
    #             text = re.sub(r'\s+', ' ', text)
                
    #             # Remove non-word characters and non-ASCII characters
    #             text = re.sub(r'[^\w\s.,/()<>]|[^ -~]', '', text)

    #             # Tokenize text and remove stopwords
    #             words = nltk.word_tokenize(text)
    #             stop_words = set(nltk.corpus.stopwords.words('english'))
    #             filtered_words = [word for word in words if word.lower() not in stop_words]
    #             cleaned_text = ' '.join(filtered_words)

    #             # Find the index of 'subject' in cleaned text
    #             subject_index = cleaned_text.find('subject')
    #             if subject_index != -1:
    #                 # Split text into two parts based on 'subject'
    #                 first_part = cleaned_text[:subject_index].strip()
    #                 second_part = cleaned_text[subject_index:].strip()
    #                 return first_part, second_part
    #             else:
    #                 return "", cleaned_text
    #         else:
    #             # Return None if 'mv' not found in text
    #             logging.error("Email doesn't contain MV or M.V. or M/V")
    #             return None
    #     except Exception as e:
    #         logging.error("Error occurred during email cleaning: %s" % e)
    #         return None
        
        
    def __decode_into_text(self, text):
        """Checks and decodes the base64 to text"""
        try:
            decoded_bytes = base64.b64decode(text)
            decoded_text = decoded_bytes.decode('utf-8')
            return decoded_text
        except Exception as e:
            logging.error("Given input is not in base64 form")
                
            
    
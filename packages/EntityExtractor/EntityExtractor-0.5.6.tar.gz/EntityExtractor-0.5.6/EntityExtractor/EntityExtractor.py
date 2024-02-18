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
from .Load_Second_Model import LoadSecondModel
from .Load_Third_Model import LoadThirdModel
from .Load_First_Model import LoadModel

logging.basicConfig(level=logging.INFO) 

class EntityExtractor(LoadModel, LoadSecondModel, LoadThirdModel):

    def __init__(self, text):
        super().__init__()
        self.__text = text
        self.__nlp_first = self._LoadModel__get_modal_instance()
        self.__nlp_second = self._LoadSecondModel__get_modal_instance()
        self.__nlp_third = self._LoadThirdModel__get_modal_instance()
        self.__decoded_text = self._LoadModel__decode_into_text(self.__text)
        self.__cleaned_text_parts = self._LoadModel__clean_email(self.__decoded_text)

    def extract_entities(self):
        try:
            entities_dict = defaultdict(list)

            # with LoadModel._LoadModel__lock:
            doc = self.__nlp_first(self.__cleaned_text_parts)
            for ent in doc.ents:
                entities_dict[ent.label_].append(ent.text)

        # with LoadSecondModel._LoadSecondModel__lock:
            doc = self.__nlp_second(self.__cleaned_text_parts)
            for ent in doc.ents:
                entities_dict[ent.label_].append(ent.text)

        # with LoadThirdModel._LoadThirdModel__lock:
            doc = self.__nlp_third(self.__cleaned_text_parts)
            for ent in doc.ents:
                entities_dict[ent.label_].append(ent.text)

            return entities_dict
        except Exception as e:
            logging.error("Error %s", e)
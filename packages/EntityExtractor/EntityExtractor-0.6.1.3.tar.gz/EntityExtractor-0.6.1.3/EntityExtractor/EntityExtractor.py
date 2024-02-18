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
from concurrent.futures import ThreadPoolExecutor
from .Load_Second_Model import LoadSecondModel
from .Load_Third_Model import LoadThirdModel
from .Load_First_Model import LoadModel
import asyncio

logging.basicConfig(level=logging.INFO) 

# class GetArguments:
#     def __init__(self,res:dict) -> None:
#         self.res = res

#     def get_vessel_name(self):
#         return self.res["VESSEL_NAME"]
    
#     def get_imo(self):
#         if len(self.res['IMO']) != 0 :
#             imo_numbers = []
#             for item in self.res['IMO']:
#                 numbers = re.sub(r'\D', '', item)
#                 imo_numbers.append(numbers)
#             return imo_numbers  
    
#     def get_dwt(self):
#         return self.res['DWT']
    
#     def get_open_area(self):
#         return self.res["OPEN AREA"]
    
#     def get_open_date(self):
#         return self.res['OPEN DATE']
    
#     def get_flag(self):
#         return self.res['FLAG']
    
#     def get_loa(self):
#         return self.res["LOA"]
    
#     def get_beam(self):
#         return self.res['BEAM']
    
#     def get_hatches(self):
#         return self.res['HATCHES']
    
#     def get_cranes(self):
#         return self.res['CRANES']
    
#     def get_bod(self):
#         return self.res["BOD"]
    
#     def get_sea_cons(self):
#         return self.res['SEA CONSUMPTION']
    
#     def get_port_cons(self):
#         return self.res['PORT CONSUMPTION']
    
#     def get_scrubber(self):
#         if len(self.res['SCRUBBER']) != 0 :
#             return 1
#         else:
#             return 0
        

class ThreadPoolManager:
    _instance = None

    def __new__(cls, max_workers=3):
        if cls._instance is None:
            cls._instance = super(ThreadPoolManager, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=max_workers)
        return cls._instance

class EntityExtractor(LoadModel, LoadSecondModel, LoadThirdModel):

    def __init__(self, text):
        super().__init__()
        self.__text = text
        self.__nlp_first = self._LoadModel__get_modal_instance()
        self.__nlp_second = self._LoadSecondModel__get_modal_instance()
        self.__nlp_third = self._LoadThirdModel__get_modal_instance()
        self.__decoded_text = self._LoadModel__decode_into_text(self.__text)
        self.__cleaned_text_parts = self._LoadModel__clean_email(self.__decoded_text)
        self.__executor = ThreadPoolManager().executor

    def process_nlp(self, nlp, entities_dict):
        doc = nlp(self.__cleaned_text_parts[1])
        for ent in doc.ents:
            entities_dict[ent.label_].append(ent.text)

    def extract_entities(self):
        entities_dict = defaultdict(list)
        futures = []
        for nlp_func in [self.__nlp_first, self.__nlp_second, self.__nlp_third]:
            future = self.__executor.submit(self.process_nlp, nlp_func, entities_dict)
            futures.append(future)

        for future in futures:
            future.result()
        return entities_dict
    
# class EntityExtractor(LoadModel, LoadSecondModel, LoadThirdModel):

#     def __init__(self, text):
#         super().__init__()
#         self.__text = text
#         self.__nlp_first = self._LoadModel__get_modal_instance()
#         self.__nlp_second = self._LoadSecondModel__get_modal_instance()
#         self.__nlp_third = self._LoadThirdModel__get_modal_instance()
#         self.__decoded_text = self._LoadModel__decode_into_text(self.__text)
#         self.__cleaned_text_parts = self._LoadModel__clean_email(self.__decoded_text)
#     def process_nlp(self, nlp, entities_dict):
#         doc = nlp(self.__cleaned_text_parts[1])
#         for ent in doc.ents:
#             entities_dict[ent.label_].append(ent.text)

#     def extract_entities(self):

#         entities_dict = defaultdict(list)
#         threads = []

#         for nlp_func in [self.__nlp_first, self.__nlp_second, self.__nlp_third]:
#             thread = threading.Thread(target=self.process_nlp, args=(nlp_func, entities_dict))
#             thread.start()
#             threads.append(thread)

#         for thread in threads:
#             thread.join()
#         return GetArguments(entities_dict)
    



    
    
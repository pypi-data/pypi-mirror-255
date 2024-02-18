import threading
import re
import nltk 
from bs4 import BeautifulSoup 
from nltk.corpus import stopwords
import spacy
from collections import defaultdict
import base64
import os
from spacy.tokens import DocBin
import requests
import zipfile
import logging
from concurrent.futures import ThreadPoolExecutor
from Load_Second_Model import LoadSecondModel
from Load_Third_Model import LoadThirdModel
from Load_First_Model import LoadModel , PreprocessText


logging.basicConfig(level=logging.INFO) 

class GetArguments:
    def __init__(self,res:dict) -> None:
        self.res = res

    def get_vessel_name(self):
        if len(self.res.get('VESSEL_NAME',[])) != 0:
            words_to_remove = ['mv', '.', "\\", ","]
            output_list = []
            seen = set()  
            for string in self.res['VESSEL_NAME']:
                cleaned_string = ' '.join(word for word in string.split() if word not in words_to_remove)
                if cleaned_string not in seen:
                    output_list.append(cleaned_string)
                    seen.add(cleaned_string) 
            return output_list
        else:
            return None


    
    def get_imo(self):
        if len(self.res.get('IMO',[])) != 0 :
            imo_numbers = []
            for item in self.res['IMO']:
                numbers = re.sub(r'\D', '', item)
                imo_numbers.append(numbers)
            return imo_numbers  
    
    def get_dwt(self):
        if len(self.res.get('DWT',[])) != 0:
            words_to_remove = ['deadweight', 'dwt', 'dwat', 'sdwat', 's.dwat', 'sdwt', 's.dwt', 'dead', 'weight']
            output_list = []
            seen_set = set()  # To keep track of seen items for efficient duplicate checking
            for string in self.res['DWT']:
                cleaned_string = ' '.join(word for word in string.split() if word.lower() not in words_to_remove)
                if cleaned_string not in seen_set:  # Check if the cleaned string is not seen before
                    output_list.append(cleaned_string)
                    seen_set.add(cleaned_string)  # Add the cleaned string to seen set
            return output_list
        else:
            return None

    
    def get_open_area(self):
        if len(self.res.get('OPEN AREA',[])) != 0:
            output_list = []
            for string in self.res['OPEN AREA']:
                cleaned_string = ' '.join(word for word in string.split() if word not in ['open'])
                output_list.append(cleaned_string)
            return output_list
        else:
            return None
    
    def get_open_date(self):
        if len(self.res.get('OPEN DATE',[])) != 0:
            return self.res['OPEN DATE']
        else:
            return None
        
    def get_build_year(self):
        if len(self.res.get('BUILD YEAR',[])) != 0:
            words_to_remove = ['built','blt','build','b','builder']
            output_list = []
            for string in self.res['BUILD YEAR']:
                cleaned_string = ' '.join(word for word in string.split() if word not in words_to_remove)
                output_list.append(cleaned_string)
            return output_list
        else:
            return None
        
    def get_flag(self):
        if len(self.res.get('FLAG',[])) != 0:
            words_to_remove = ['flag','flg']
            output_list = []
            for string in self.res['FLAG']:
                cleaned_string = ' '.join(word for word in string.split() if word not in words_to_remove)
                output_list.append(cleaned_string)
            return output_list
        else:
            return None
    
    def get_loa(self):
        if len(self.res.get('LOA',[])):
            return self.res["LOA"]
        else:
            return None
        
    def get_beam(self):
        if len(self.res.get('BEAM',[])):
            return self.res['BEAM']
        else:
            return None
        
    def get_hatches(self):
        if len(self.res.get('HATCHES',[])):
            return self.res['HATCHES']
        else:
            None

    def get_cranes(self):
        if len(self.res.get('CRANES',[])) != 0:
            words_to_remove = ['cranes', 'crane', 'cr', 'hydraulic','electro','electro-', 'deck', 'abt','four','electrohydraulic','macgregor' , 'swl' , 'tts']
            output_list = []
            for string in self.res['CRANES']:
                cleaned_string = ' '.join(word for word in string.split() if word not in words_to_remove)
                output_list.append(cleaned_string)
            return output_list
        else:
            return None

    
    def get_bod(self):
        if len(self.res.get("BOD",[]))!=0:
            return self.res["BOD"]
        else:
            None
    
    def get_sea_cons(self):
        if len(self.res.get('SEA CONSUMPTION'),[])!=0:
            return self.res["SEA CONSUMPTION"]
        else:
            None
    
    def get_port_cons(self):
        if len(self.res.get('PORT CONSUMPTION',[]))!=0:
            return self.res['PORT CONSUMPTION']
        else:
            None
    
    def get_scrubber(self):
        if len(self.res.get('SCRUBBER',[])) != 0 :
            return 1
        else:
            return 0
        


from functools import partial

class ThreadPoolManager:
    _instance = None

    def __new__(cls, max_workers=3):
        if cls._instance is None:
            cls._instance = super(ThreadPoolManager, cls).__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=max_workers)
        return cls._instance

class EntityExtractor(LoadModel, PreprocessText , LoadSecondModel, LoadThirdModel):

    def __init__(self):
        super().__init__()
        self.__nlp_first = self._LoadModel__get_modal_instance()
        self.__nlp_second = self._LoadSecondModel__get_modal_instance()
        self.__nlp_third = self._LoadThirdModel__get_modal_instance()
        self.__executor = ThreadPoolExecutor()

    def process_nlp(self, nlp, entities_dict, text):
        doc = nlp(text)
        for ent in doc.ents:
            entities_dict[ent.label_].append(ent.text)

    def extract_entities(self, text):
        entities_dict = defaultdict(list)
        futures = []

        decoded_text = self._PreprocessText__decode_into_text(text)
        cleaned_text_parts = self._PreprocessText__clean_email(decoded_text)
        if cleaned_text_parts is None:
            return GetArguments(entities_dict)
        else:
                    
            text_to_process = cleaned_text_parts[1]

            chunk_size = len(text_to_process) // 2
            overlap = 20
            chunks = [text_to_process[i:i+chunk_size+overlap] for i in range(0, len(text_to_process), chunk_size)]

            for nlp_func in [self.__nlp_first, self.__nlp_second, self.__nlp_third]:
                for chunk in chunks:
                    future = self.__executor.submit(self.process_nlp, nlp_func, entities_dict, chunk)
                    futures.append(future)

            for future in futures:
                future.result()
            
            return GetArguments(entities_dict)



    
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
    



    
    
import os
from PIL import Image,ImageEnhance
import pytesseract
import cv2 
import numpy as np
import json
from nltk import edit_distance 
import concurrent.futures
import time
from dataclasses import dataclass,field
from typing import Any, List
import logging
import argparse
@dataclass(slots=True,kw_only=True,init=True)

class OCR_Config:
    image_path:str
    json_path:str
    annot_path:str
    show_crop_reg:bool=False
    Json_Dir:str=r""
    save_json:bool=False
    show_output_image:bool=False
    dpi:int=500
    contrast:int=500
    preprop_img_out:bool=False # Enable it will preprocess imain binary
    conf_file:str=r"config.json"
    search_spec_item:bool=False
    spec_items: List[str] = field(default_factory=list)
    save_crop_reg:bool=False
    crprgn_cust_folder:str=r""
    save_log:bool=True
    log_fp:str=r""
    psm:int=6
    oem:int=3
    lang:str="eng"
    whl:str=""
    bl:str=""
    use_config:bool=False
 
    @classmethod
    def set_tesseract_path(cls, path):
        pytesseract.pytesseract.tesseract_cmd = path
        
    def record_log(self, lt=logging.INFO):
        try:
            # Create a log directory with the current date and time
            log_dir = os.path.join(os.getcwd(), "logs", time.strftime("%Y-%m-%d_%H-%M-%S"))
            os.makedirs(log_dir, exist_ok=True)

            # Set the full log file paths
            info_log_path = os.path.join(log_dir, "info_logs.txt")
            error_log_path = os.path.join(log_dir, "error_logs.txt")

            # Configure logging for info messages
            info_handler = logging.FileHandler(info_log_path)
            info_handler.setLevel(logging.INFO)
            info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            info_handler.setFormatter(info_formatter)
            logging.getLogger().addHandler(info_handler)

            # Configure logging for error messages
            error_handler = logging.FileHandler(error_log_path)
            error_handler.setLevel(logging.ERROR)
            error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            error_handler.setFormatter(error_formatter)
            logging.getLogger().addHandler(error_handler)

            logging.info(f"Info logs will be saved to: {info_log_path}")
            logging.info(f"Error logs will be saved to: {error_log_path}")

            # Create a text file in the log directory
            text_file_path = os.path.join(log_dir, "log_info.txt")
            with open(text_file_path, 'w') as text_file:
                text_file.write(f"Additional information: Logs are saved to {info_log_path} (Info) and {error_log_path} (Error)")

        except Exception as e:
            print(f"Error occurred while setting up logging: {e}")


 


    @classmethod
    def ocr_read_conf(cls,data)->'OCR_Config':
        try:
            return cls(**data)
        except Exception as e:
            logging.error(f"Some error occur while load config",e)
    

class Ocr_Function(OCR_Config):
    def __init__(self, *args, **kwargs) -> None:
   
        super().__init__(*args, **kwargs)

 
    @classmethod
    def ocr_function_read_conf(cls, data) -> 'Ocr_Function':
        try:
            return cls(**data)
        except Exception as e:
            logging.error("Some error occurred while loading config for Ocr_Function", e)


        
    @classmethod       
    def load_classes(cls,classes_path):
        with open(classes_path, 'r') as file:
            classes = file.read().strip().split('\n')
        return classes
    
    @classmethod
    def load_json(cls, path) -> dict:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
            return data

        
    def ocr_v2(self, impath, psm=6, oem=3, lang="eng", whl="", bl=""):
        my_config = f"--psm {psm} --oem {oem}"
        if whl != "":
            my_config += " -c tessedit_char_whitelist={whl}"
        if bl != "":
            my_config += " -c tessedit_char_blacklist={bl}"
        # my_config = f"--psm {psm} --oem {oem}"
        print(my_config, lang)
        txt = pytesseract.image_to_string(impath, config=my_config, lang=lang)
        return txt
    
    def preprocess_image(self,img_array, contrast=0.8, dpi=500,CustomPreProcess=None):
        if CustomPreProcess is None:
            # Convert the image array to PIL Image
            img = Image.fromarray(img_array)

            # Step 1: Scaling of image to the right size (300 DPI)
            if 'dpi' in img.info:
                img = img.convert("RGB")
                img = img.resize((int(img.width * dpi / img.info['dpi'][0]), int(img.height * dpi / img.info['dpi'][1])))
            else:
                img = img.convert("RGB")
                img = img.resize((int(img.width * dpi / 300), int(img.height * dpi / 300)))

            # Step 2: Increasing contrast of image
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)  # Adjust the enhancement factor as needed

            # Convert the image to grayscale
            img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

            # Binarization using Otsu's thresholding
            _, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            return img_binary
        else:
            return CustomPreProcess(img_array)
        
 


    def draw_boundbox(self,bb_data, cobj, img, show_crop_reg, img_copy,dpi=500,contrast=500,show_ppi=False,spec_field=False,spec_field_items=[],cust_cbf=None):
        ml_data = []
        for bbd in bb_data:
            components = bbd.strip().split()
            object_class = cobj[int(components[0])]
            x, y, width, height = map(float, components[1:])
            x1 = int((x - width / 2) * img.shape[1])
            y1 = int((y - height / 2) * img.shape[0])
            x2 = int((x + width / 2) * img.shape[1])
            y2 = int((y + height / 2) * img.shape[0])
            
            if spec_field==False:
                cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img_copy, f"Class: {object_class}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                if object_class in spec_field_items:
                    cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img_copy, f"Class: {object_class}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
            
            cropped_region = img[y1:y2, x1:x2]
            if show_ppi:
                cropped_region = self.preprocess_image(cropped_region,dpi=dpi,contrast=contrast,CustomPreProcess=cust_cbf)

            if show_crop_reg:
                cv2.imshow("Cropped Region", cropped_region)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        
            ml_data.append([cropped_region, object_class])

    
        return ml_data
    
    @classmethod
    def load_conf(cls, conf_path):
        with open(conf_path, 'r') as lc:
            jv = json.load(lc)
            return jv

        

    def OCR_All_Field(self,cust_img_ppf=None):
        try:
            txt=""
            defconf = ""
            img = cv2.imread(self.image_path)
            imnamea = os.path.splitext(os.path.basename(self.image_path))[0]

            jsom_fp = os.path.join(self.json_path, imnamea + ".json")
            anot_fp = os.path.join(self.annot_path, imnamea + ".txt")
            logging.info("Open image  >>>>>", imnamea, " from ", self.image_path, " And json name is ", jsom_fp)
            self.record_log(logging.INFO)
            

            if os.path.exists(self.image_path) and os.path.exists(jsom_fp) and os.path.exists(anot_fp):
                jdata = self.load_json(jsom_fp)
                logging.info(f"Json data = {jdata}")
                logging.info(f"File paths exist for {self.image_path}, json {jsom_fp}, and annotation {anot_fp}")
                self.record_log(logging.INFO)
            else:
                logging.error(f"File paths do not exist for {self.image_path}, json {jsom_fp}, and annotation {anot_fp}")
                self.record_log(logging.ERROR)
                return

            if self.conf_file != "":
                defconf = self.load_conf(self.conf_file)
                logging.info("config====> ", defconf)
                self.record_log(logging.INFO)

            img_copy = img.copy()
            with open(anot_fp, 'r') as arp:
                bb_data = arp.readlines()

            data_dict = {}
            cobj = self.load_classes(os.path.join(self.annot_path, "classes.txt"))
            class_conf=""
            ml_data = self.draw_boundbox(bb_data=bb_data, img=img, show_crop_reg=self.show_crop_reg, cobj=cobj, img_copy=img_copy, dpi=self.dpi, contrast=self.contrast, show_ppi=self.preprop_img_out, spec_field=self.search_spec_item, spec_field_items=self.spec_items,cust_cbf=cust_img_ppf)

            for ml in ml_data:
                cropped_region, object_class = ml

                if self.search_spec_item == True:

                    if object_class in self.spec_items:
                        
                        if self.use_config:

                            class_conf = defconf.get(object_class, defconf.get("default", {}))
                            logging.info(f"Config selected: {class_conf}")
                            self.record_log(logging.INFO)

                            txt = self.ocr_v2(impath=cropped_region, psm=class_conf.get("spsm", self.psm), oem=class_conf.get("soem", self.oem),
                                            lang=class_conf.get("slang", self.lang), whl=class_conf.get("whl", ""), bl=class_conf.get("bl", ""))
                        else:

                            txt = self.ocr_v2(impath=cropped_region, psm=self.psm, oem=self.oem,lang=self.lang, whl=self.whl, bl=self.bl)
                            
                        txt = txt.replace("\n", "")
                        txt = txt.replace("\f", "")
                        logging.info(f"Original txt {txt}")
                        self.record_log(logging.INFO)

                        if object_class in jdata:
                            minspace = edit_distance(txt, jdata[object_class])
                            
                            logging.info(f"image name {imnamea}\n Class  {object_class}, \n OCR val {txt}\nEdit distance  {minspace}\n Original txt \n{jdata[object_class]}")
                            self.record_log(logging.INFO)
                            
                        else:
                            minspace = -1
                            logging.error(f"Class: {object_class} not found in JSON data")
                            self.record_log(logging.ERROR)

                        data_dict[object_class] = {
                            "Title": object_class,
                            "OCR text": txt,
                            "Original text": str(jdata.get(object_class, "")),
                            "Edit Distance": minspace
                        }
                else:
                    class_conf = defconf.get(object_class, defconf.get("default", {}))
             
                    logging.info(f"Config selected: {class_conf}")
                    self.record_log(logging.INFO)
                    if self.use_config:
                        txt = self.ocr_v2(impath=cropped_region, psm=class_conf.get("spsm", self.psm), oem=class_conf.get("soem", self.oem),
                                        lang=class_conf.get("slang", self.lang), whl=class_conf.get("whl", ""), bl=class_conf.get("bl", ""))
                    else:
                        txt = self.ocr_v2(impath=cropped_region, psm=self.psm, oem=self.oem,lang=self.lang, whl=self.whl, bl=self.bl)                       


                    txt = txt.replace("\n", "")
                    txt = txt.replace("\f", "")
                    print(f"Original txt {txt}")

                    if object_class in jdata:
                        minspace = edit_distance(txt, jdata[object_class])
                        print(
                            f"image name {imnamea}\n Class  {object_class}, \n OCR val {txt}\nEdit distance  {minspace}\n Original txt \n{jdata[object_class]}")
                    else:
                        minspace = -1
                        print(f"Class: {object_class} not found in JSON data")

                    data_dict[object_class] = {
                        "Title": object_class,
                        "OCR text": txt,
                        "Original text": str(jdata.get(object_class, "")),
                        "Edit Distance": minspace
                    }
                if self.save_crop_reg==True:
                    
                    if self.crprgn_cust_folder != "":
                        copf1 = os.path.join(self.crprgn_cust_folder, imnamea)
                        copimp = os.path.join(copf1, f"{txt}.png")

                        # Check if the parent directory exists, if not, create it
                        if not os.path.exists(copf1):
                            os.makedirs(copf1)

                        if os.path.exists(copimp):
                            print(f"Image {imnamea} exists at path {copimp}")
                            continue
                        else:
                            cv2.imwrite(copimp, cropped_region)
                    else:
                        dp=r"crop_regions"
                        copf1=os.path.join(dp,imnamea)
                        copimp=os.path.join(copf1,f"{txt}.png")
                        # Check if the parent directory exists, if not, create it
                        if not os.path.exists(copf1):
                            os.makedirs(copf1)

                        if os.path.exists(copimp):
                            print(f"Image {imnamea} exists at path {copimp}")
                            continue
                        else:
                            cv2.imwrite(copimp, cropped_region)

                mjson = {self.image_path: data_dict}

            if self.save_json:
                if not os.path.exists(self.Json_Dir):
                    os.mkdir(self.Json_Dir)
                with open(f"{self.Json_Dir}/{imnamea}_ocr_result.json", 'w') as jsfp:
                    json.dump(mjson, jsfp, ensure_ascii=False, indent=2)
                print(f"JSON saved to {self.Json_Dir}/{imnamea}_ocr_result.json")

            if self.show_output_image:
                cv2.imshow("Processed Image", img_copy)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        except Exception as e:
            logging.error("Some error occurred while OCR:", e)
            self.record_log(logging.ERROR)


    def ocr_entirefile(self,path,cust_preprocess_func=None,imgformat:list=[".jpg",".png"]):
        if os.path.exists(path=path):
            for root,_,file in os.walk(path):
                for f in file:
                    bp=os.path.join(root,f)
                    efe=os.path.splitext(bp)
                    if efe[1] in imgformat:
                        logging.info(f"Start proceqss at >>>>> {bp}")
                        self.image_path=bp
                        self.OCR_All_Field(cust_img_ppf=cust_preprocess_func)
                    else:
                        logging.error("Format of image not found")
  
  
 
class json_conf_load:
    def __init__(self, json_fp) -> None:
        if os.path.exists(json_fp):
            with open(json_fp, 'r') as jf:
                con = json.load(jf)
                self.ocr_fun_instance = Ocr_Function.ocr_function_read_conf(con)
        else:
            logging.error("Error: cannot find json config file.")

    def get_ocr_function_instance(self):
        return self.ocr_fun_instance


 
 
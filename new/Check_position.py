from glob import glob
import cv2
import pandas as pd
import numpy as np
from os import path as osp
import sys
from bs4 import BeautifulSoup as bs 

def read_xml(xml_file_path):
    dataframe = {'name':[], 'xmin':[], 'ymin':[], 'xmax':[], 'ymax':[]}
    #read xml_file
    with open(xml_file_path, 'r') as f:
        data = f.read()
    
    Bs_data = bs(data, "xml")
    
    objects = Bs_data.find_all('object')
    #run each object
    for Object in objects:
        name, xmin, ymin, xmax, ymax = get_object_info(Object)
        
        #append data
        if name == 'without_mask':
            dataframe['name'].append(1)
        else:
            dataframe['name'].append(-1)
        
        dataframe['xmin'].append(xmin)
        dataframe['ymin'].append(ymin) 
        dataframe['xmax'].append(xmax) 
        dataframe['ymax'].append(ymax) 
    return dataframe

def get_object_info(Object):
    name = Object.find('name').text
    bndbox = Object.find('bndbox')
    xmin = int(bndbox.find('xmin').text)
    ymin = int(bndbox.find('ymin').text)
    xmax = int(bndbox.find('xmax').text)
    ymax = int(bndbox.find('ymax').text)
    return name, xmin, ymin, xmax, ymax

def click_event(event, x, y, flags, params):
    global temp_min
    global temp_max
    global temp_img
    #check left_click
    if event == cv2.EVENT_LBUTTONDOWN:
        
        cv2.circle(temp_img, (x,y),1, (255, 0, 0), 2)
        cv2.imshow('image', temp_img)
        temp_min = (x,y)
    
    #check right_click
    if event == cv2.EVENT_RBUTTONDOWN:
        
        cv2.circle(temp_img, (x,y),1, (255, 255, 0), 2)
        cv2.imshow('image', temp_img)
        temp_max = (x,y)
        
def process(image_path, save_folder, annotations_type='xml'):
    global temp_min
    global temp_max
    global temp_img
    #define
    name = image_path.split('\\')[-1].split('.')[0]
    annotations_path = osp.join(annotations_folder, name+'.'+annotations_type)
    save_path = osp.join(save_folder, name+'.csv')
    color = (0, 0, 255)
    thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    #open image
    raw_img = cv2.imread(image_path, 1)
    temp_img = raw_img.copy()
    
    #read xml
    data = read_xml(annotations_path)
    
    remove = False
    #run for each objects
    for idx,(name, xmin, ymin, xmax, ymax) in enumerate(zip(data['name'], data['xmin'], data['ymin'], data['xmax'], data['ymax'])):
        #bonding object
        tag = 'Unknow'
        temp_min = (xmin, ymin)
        temp_max = (xmax, ymax)
        finish = False
        #run until next or exit
        while (True):
            #show image
            (xmin, ymin) = temp_min
            (xmax, ymax) = temp_max
            temp_img = raw_img.copy()
            img = raw_img.copy()
            img = cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness)
            cv2.putText(img, tag, (xmin, ymin-5),font, 0.5, color, thickness)
            
            cv2.imshow('image', img)
            #cv2.imshow(name, img)
            
            key = cv2.waitKey(0)
            
            #key option
            if (key==13):
                #need to be tag
                if not finish:
                    tag = 'Tag???'
                    continue
                raw_img = img
                break
            elif key==27:
                cv2.destroyAllWindows()
                return None
            elif key== 49:
                data['name'][idx] = 1
                tag = 'No Mask'
                finish = True
            elif key == 50:
                data['name'][idx] = 2
                tag = 'Homemade mask'
                finish = True
            elif key == 51:
                data['name'][idx] = 3
                tag = 'Surgical mask'
                finish = True
            elif key == 52:
                data['name'][idx] = 4
                tag = 'N95 mask'
                finish = True
            elif key == 53:
                data['name'][idx] = 5
                tag = 'P95 mask'
                finish = True
            elif key == 54:
                data['name'][idx] = 6
                tag = 'Wearing wrong'
                finish = True


            elif key == 110:    

                cv2.setMouseCallback('image', click_event)
                #cv2.setMouseCallback(name, click_event)

            elif key==8:
                data['name'][idx] = -1
                remove = True
                break
    cv2.waitKey(0)          
    cv2.destroyAllWindows()
    if remove:
        for idx,name in enumerate(data['name']):
            if name==-1:
                data['name'].pop(idx)
                data['xmin'].pop(idx)
                data['ymin'].pop(idx)
                data['xmax'].pop(idx)
                data['ymax'].pop(idx)
    dataFrame = pd.DataFrame(data)
    dataFrame.to_csv(save_path, index = False)
    return data


if __name__ == "__main__":
    annotations_folder = r'D:\annotations'
    images_folder = r'D:\images'
    save_folder = r'D:\set'
    global temp_min
    global temp_max
    global temp_img
    
    for img_path in glob(images_folder+'\*'):
        process(img_path,save_folder)
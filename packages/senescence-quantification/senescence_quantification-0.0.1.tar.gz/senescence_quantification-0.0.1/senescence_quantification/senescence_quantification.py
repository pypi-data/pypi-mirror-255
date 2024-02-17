import numpy as np
import pandas as pd
from plantcv import plantcv as pcv
import joblib
import matplotlib.pyplot as plt
import cv2 

def get_model(model_name):
    try:
        if(model_name=='KNN'):
            model = joblib.load('data/knn_40_1000.sav')

        elif(model_name=='DecisionTree'):
            model=joblib.load('data/tree_1000_m.sav')

        elif(model_name=='RandomForest'):
            model=joblib.load('data/rf_1000.sav')

        elif(model_name=='GradientBoosting'):
            model=joblib.load('data/gb_50_1000.sav')

        elif(model_name=='MLP'):
            model=joblib.load('data/mlp_1000.sav')

        elif(model_name=='NaiveBayes'):
            model=joblib.load('data/nb_1000.sav')

        else:
            model=0
        return model
    except:
        return 0
        
    
    
def process_img(model_name, img_path):
    
    """This function computes senescence percentage from
    an input wheat plant image. After computing senescence percetnage for plant, 
    it return into five categories, Dry, Yellow,Pale Yellow,Light Green, and Green.
    In addition it provides total pixels for wheat plant.
    
    Parameters:
    ---------------------
    img_path (string): file path of image
    model_name(string): Accept one value among the followings:
    [KNN, DecisionTree, RandomForest, GradientBoosting, MLP, NaiveBayes]
    
    
    Returns:
    int:dict


   """
    
    # read input image
    img, path, file = pcv.readimage(img_path)
    # segment require portion
    img = img[950:4000, 1250:3000]
    # get img attributes
    width, depth, height = img.shape
    
    # flatten image for faster predictions
    flattened_img = img.reshape(-1, 3)
    
    # call the get_model function to select the classfier
    model=get_model(model_name)

    
    predictions = model.predict(flattened_img)
    # get the total prediction in each class
    classes = np.unique(predictions, return_counts=True)
    classes_arrary = classes[0]
    loc_0 = 'null'
    loc_1 = 'null'
    loc_2 = 'null'
    loc_3 = 'null'
    loc_4 = 'null'
    
    default_loc = 0
    
    # get the position of five classes in predicted array 
    
    for flag in classes_arrary:
        if flag == 0:
            loc_0 = default_loc
        if flag == 1:
            loc_1 = default_loc
        if flag == 2:
            loc_2 = default_loc
        if flag == 3:
            loc_3 = default_loc
        if flag == 4:
            loc_4 = default_loc
        
        default_loc += 1
        
    dark_pix = 0
    yellow_pix = 0
    pale_pix = 0
    light_green_pix = 0
    green_pix = 0
    
    # get total pixels predicted in each class
    if loc_0 != 'null':
        dark_pix = classes[1][loc_0]
    if loc_1 != 'null':
        yellow_pix = classes[1][loc_1]
    if loc_2 != 'null':
        pale_pix = classes[1][loc_2]
    if loc_3 != 'null':
        light_green_pix = classes[1][loc_3]
    if loc_4 != 'null':
        green_pix = classes[1][loc_4]
        
        
    total_pix = dark_pix + yellow_pix + pale_pix + light_green_pix + green_pix
    dark_pix_per=dark_pix * 100 / total_pix
    yellow_pix_per=yellow_pix * 100 / total_pix
    pale_yellow_pix_per=pale_pix * 100 / total_pix
    light_green_pix_per=light_green_pix * 100 / total_pix
    green_pix_per=green_pix * 100 / total_pix
    
    senes_dict={
        'dark pixel percentage':dark_pix_per,
        'yellow pixel percentage':yellow_pix_per,
        'pale yellow pixel percentage':pale_yellow_pix_per,
        'light green pixel percentage':light_green_pix_per,
        'green pixel percentage':green_pix_per,
        'total plant pixels':total_pix
    }
    print(senes_dict)
    
    mask_dark = np.zeros((width * depth), dtype=np.uint8)
    mask_yellow = np.zeros((width * depth), dtype=np.uint8)
    mask_light_yellow = np.zeros((width * depth), dtype=np.uint8)
    mask_light_green = np.zeros((width * depth), dtype=np.uint8)
    mask_green = np.zeros((width * depth), dtype=np.uint8)
    mask_white = np.zeros((width * depth), dtype=np.uint8)
    mask_dark[np.where(predictions == 0)] = 255
    mask_yellow[np.where(predictions == 1)] = 255
    mask_light_yellow[np.where(predictions == 2)] = 255
    mask_light_green[np.where(predictions == 3)] = 255
    mask_green[np.where(predictions == 4)] = 255
    mask_white[np.where(predictions == 5)] = 255
    mask_white[np.where(predictions == 6)] = 255
    mask_dark = mask_dark.reshape((width, depth))
    mask_yellow = mask_yellow.reshape((width, depth))
    mask_light_yellow = mask_light_yellow.reshape((width, depth))
    mask_light_green = mask_light_green.reshape((width, depth))
    mask_green = mask_green.reshape((width, depth))
    mask_white = mask_white.reshape((width, depth))
    mask_color = pcv.visualize.colorize_masks(
        masks=[mask_dark, mask_yellow, mask_light_yellow, mask_light_green, mask_green, mask_white],
        colors=['red', 'yellow', 'blue', 'orange', 'green', 'white'])
    cv2.imshow('coloured mask',mask_color)
    cv2.waitKey(0) 
    cv2.destroyAllWindows() 
    
    return senes_dict


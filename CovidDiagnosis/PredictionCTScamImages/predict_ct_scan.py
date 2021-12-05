import cv2
import tensorflow as tf
import sys
import os
categories = ["covid19_scan","normal_scan"]

def prepare(filepath):
    IMG_SIZE = 150
    img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(img_array, (IMG_SIZE,IMG_SIZE))
    return new_array.reshape(-1,IMG_SIZE,IMG_SIZE,1)

model = tf.keras.models.load_model('PredictionCTScamImages/covid19_pneumonia_detection_cnn.model')
filepath = sys.argv[1]
os.path.join('G:/Python2021Workspace/CovidDiagnosis/')
path = os.path.abspath('G:/Python2021Workspace/CovidDiagnosis/'+filepath)
print("My FIle Path is ",path)
#prediction = model.predict([prepare('PredictionCTScamImages/normal_ct_scan.png')])
prediction = model.predict([prepare(path)])
print("My Predictions=",prediction)
print(categories[int(prediction[0][0])])

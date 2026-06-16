from django.shortcuts import render
import os
from django.conf import settings
import numpy as np
import requests
import json
import warnings
warnings.filterwarnings('ignore')
from sklearn.ensemble import RandomForestClassifier
import numpy as np

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Load the trained model
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification


# Load the dataset (for consistency in feature scaling)
df = pd.read_csv('health_dataset.csv')
X = df[['Temperature', 'ECG']].values
y = df[['Label']].values
clf = RandomForestClassifier(max_depth=2, random_state=0)
clf.fit(X, y)

print(clf.predict([[0, 0]]))
# Normalize using the same scaler
#scaler = StandardScaler()
#scaler.fit(X)  # Fit on the original dataset

# Function to predict disease
def predict_disease(temperature,ecg):
    # Prepare input data
    input_data = np.array([[temperature,ecg]])
    #input_data_scaled = scaler.transform(input_data)

    # Make prediction
    prediction = clf.predict(input_data)
    print(prediction)
    # result = "Diseased" if prediction[0][0] > 0.5 else "Not Diseased"
    
    return prediction[0]

def ts_data():
    url = "https://api.thingspeak.com/channels/2077029/feeds.json?results=2"  # Replace "https://example.com" with the URL you want to make the GET request to
    try:
        response = requests.get(url)
        datas = json.loads(response.text)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
           return datas['feeds'][0]["field1"],datas['feeds'][0]["field2"],datas['feeds'][0]["field3"]
        else:
            print(f"Error: GET request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("Error:", e)

target_names = ['Healthy','Diseased']

def preprocess_image(image_path, target_size=(128, 128)):
    img = load_img(image_path, target_size=target_size)
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img, img_array
def index(request):
    return render(request,"index.html")

def about(request):
    return render(request,"about.html")

def predict(request):
    data  = ts_data()
    if data is None:
        data = [0,0]

    res = ""
    status = (data[2][1:2] == "a")
    print(status)
    return render(request,"upload.html",{"lat":data[0],"long":data[1],"result":res,'status':status})

def Patient(request):
    random_message = ""
    drugs = ['Paracitamol','Cofsils','']
    hb = temp = ecg = 0
    prescrp = "No need"
    selected_drug = ""
    if request.method =="POST":
        age = request.POST['age']
        temp = request.POST['t']
        ecg = request.POST['ecg']
        hb = request.POST['hb']
        result = predict_disease(ecg,temp)
        import random

        health_responses = [
            # Fever responses
            [
                "You are affected by fever. Stay hydrated by drinking plenty of fluids and take rest to help your body recover.",
                "Fever detected! Make sure to drink warm fluids, take over-the-counter medications if needed, and get plenty of sleep.",
                "You might be running a fever. Keep yourself cool with a damp cloth on your forehead and stay hydrated.",
                "It seems you have a fever. Take a lukewarm bath, stay in a comfortable environment, and consume light, nutritious meals.",
                "Fever symptoms detected. Try sipping herbal tea, resting in a cool place, and monitoring your temperature regularly."
            ],

            # Cough responses
            [
                "You are affected by cough. Drink warm water with honey and ginger to soothe your throat.",
                "Cough detected! Gargle with salt water and take a steam inhalation to relieve congestion.",
                "You might have a cough. Try herbal teas like peppermint or chamomile and avoid cold drinks.",
                "It seems you have a cough. Suck on lozenges and use a humidifier to keep your airways moist.",
                "Cough symptoms detected. Rest your voice, stay hydrated, and take cough syrup if needed."
            ],

            # Healthy responses
            [
                "You are healthy! Keep maintaining a balanced diet and regular exercise.",
                "All good! Your health is in great shape. Keep up the positive habits.",
                "You are perfectly healthy! Stay active and continue your wellness routine.",
                "No health issues detected. Keep eating nutritious food and staying fit.",
                "You’re in great shape! Maintain your healthy lifestyle and stay positive."
            ]
        ]

        # Selecting a random message from the 0th list (fever responses)
        random_message = random.choice(health_responses[int(result)])
        print(result)
        print(random_message)
        selected_drug = drugs[int(result)]

        # if result[1] < .3:
     
        #     prescrp = "ghasjqghgf"
        
    data = ts_data()
    print(data)
    if data is not None:
        hb = data[0]
        ecg = data[1]
        temp = data[2]
    return render(request,"patient.html",{"results":random_message,'prescrp':selected_drug,'temp':temp,'ecg':ecg,'hb':hb})
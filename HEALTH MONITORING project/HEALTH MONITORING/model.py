import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load the dataset
df = pd.read_csv('health_datas  et1.csv')

# Split features and labels
X = df[['Age', 'Temperature', 'Heartbeat', 'ECG']].values
y = df['Diseased'].values

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define the deep learning model
model = keras.Sequential([
    keras.layers.Dense(16, activation='relu', input_shape=(4,)),  # Input layer
    keras.layers.Dense(8, activation='relu'),  # Hidden layer
    keras.layers.Dense(1, activation='sigmoid')  # Output layer for binary classification
])

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=50, batch_size=8, validation_data=(X_test, y_test))

# Save the trained model
model.save('health_prediction_model2.h5')

print("Model trained and saved as 'health_prediction_model2.h5'")

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic data
num_samples = 200
age = np.random.randint(20, 80, num_samples)  # Age between 20 and 80
temperature = np.random.normal(98.6, 1.5, num_samples)  # Normal body temperature distribution
heartbeat = np.random.randint(60, 120, num_samples)  # Heart rate between 60 and 120 BPM
ecg = np.random.uniform(0.8, 1.2, num_samples)  # Simulated ECG values

# Correlation between temperature and disease (higher temp increases disease probability)
prob_disease = np.clip((temperature - 98.6) * 5 + 0.3, 0, 1)  # Probability based on temperature
diseased = np.random.binomial(1, prob_disease)  # 1 = Diseased, 0 = Not Diseased

# Create DataFrame
df = pd.DataFrame({
    'Age': age,
    'Temperature': temperature,
    'Heartbeat': heartbeat,
    'ECG': ecg,
    'Diseased': diseased
})

# Save to CSV
df.to_csv('health_dataset1.csv', index=False)

# Display first few rows
print(df.head())


from src.data_loader import load_health_data

# Load astronaut health data
df = load_health_data()

# Display the first 5 records
print("ASTRA Health Data:")
print(df.head())

# Display dataset information
print("\nDataset Shape:")
print(df.shape)

print("\nDataset Columns:")
print(df.columns.tolist())

import pandas as pd

# Load the original dataset
input_file = "data/worldbank_data.csv"  # Replace with the path to your original file
output_file = "data/worldbank_data_cleaned.csv"

# Load only necessary columns
columns_to_keep = ['INDICATOR', 'SEX', 'Country name', 'economy'] + [f'YR{year}' for year in range(2015, 2022)]
chunks = pd.read_csv(input_file, usecols=columns_to_keep, low_memory=False, chunksize=10000)

# Filter rows and save cleaned dataset
filtered_data = []

for chunk in chunks:
    # Filter rows with specific INDICATOR and SEX
    chunk_filtered = chunk[(chunk['INDICATOR'] == 'HD.HCI.AMRT') & (chunk['SEX'] == '_T')]
    filtered_data.append(chunk_filtered)

# Concatenate all chunks
cleaned_data = pd.concat(filtered_data)

# Save to a new CSV file
cleaned_data.to_csv(output_file, index=False)

print(f"Cleaned dataset saved to {output_file}.")

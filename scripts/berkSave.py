import requests
import os

# Define the base URL and the destination directory
base_url = "https://www.berkshirehathaway.com/letters/{}ltr.pdf"
save_dir = "/Users/seangroebe/Development/EmergingTech/PDFs/berkHthwyShareholders/"

# Ensure the save directory exists; create it if it doesn't
os.makedirs(save_dir, exist_ok=True)

# Loop through each year from 2005 to 2023
for year in range(2005, 2024):
    url = base_url.format(year)
    response = requests.get(url)
    
    if response.status_code == 200:
        file_name = f"{year}ltr.pdf"
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {file_name}")
    else:
        print(f"Failed to download {year}ltr.pdf (HTTP {response.status_code})")
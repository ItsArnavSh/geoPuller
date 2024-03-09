import requests
from datetime import date, timedelta
import os
import cv2


base_url = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{}/250m/6/13/13.jpg"
min_black_area = 10000  # Adjust this value based on your needs
min_white_area = 10000
start_year = 2012
current_year = 2024
month_days = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

# Create a folder to store downloaded images (if it doesn't exist)
folder_name = "MODIS_Images"
os.makedirs(folder_name, exist_ok=True)

for year in range(start_year, current_year + 1):
    image_found = False  # Flag to track if an image was found for the year

    for month in range(1, 13):
        for day in range(1, month_days[month] + 1):
            image_url = base_url.format(f"{year}-{month:02d}-{day:02d}")

            response = requests.get(image_url, stream=True)

            if response.status_code == 200:
                
                filename = f"MODIS_Terra_{year}.jpg"
                filepath = os.path.join(folder_name, filename)

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                # Read the downloaded image
                img = cv2.imread(filepath)

                # Convert the image to grayscale for easier analysis
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Threshold the image to identify black pixels
                thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]

                # Find contours (connected black regions)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Check if any large black area is present
                large_black_area = False
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area < min_black_area:
                        large_black_area = True
                        break  # Exit the loop after finding one large black area

                # Skip saving the image if a large black area is found
                if large_black_area:
                    print(f"Image ignored: Large black area detected in {filename}")
                    os.remove(filepath)  # Remove the downloaded image
                else:
                    print(f"Image saved: {filename}")
                    image_found = True
                    break  # Found an image, move to the next year
                
            response.close()
        if image_found:
            break  # Move to the next year (outer loop)
    # Now check image_found flag after the month loop

    # If no image found for the entire year, print a message
    if not image_found:
        print(f"No image found for {year}")

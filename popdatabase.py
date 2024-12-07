import os
from pymongo import MongoClient

client=MongoClient("mongodb://root:secret@localhost:27017")
db=client["Outfits"]

categories={
    "cold": {"min": -10, "max": 0},
    "cool": {"min": 1, "max": 15},
    "warm": {"min": 16, "max": 25},
    "hot": {"min": 26, "max": 40}
}
images_folder="./images"
outfit_data=[]

for category, temp_range in categories.items():
    category_folder=os.path.join(images_folder, category) 
    if os.path.exists(category_folder):
        images=[img for img in os.listdir(category_folder) if img.endswith((".jpg", ".png"))]
        for image in images:
            outfit_data.append({
                "temperature_range": temp_range,
                "weather_condition": category,
                "image_url": f"/images/{category}/{image}" 
            })
    else:
        print(f"Folder for category '{category}' does not exist. Skipping...")

if outfit_data:
    db.outfits.insert_many(outfit_data)
    print(f"Inserted "+len(outfit_data)+" entries into the database!")
else:
    print("Failed to put pics in database")

import json
import os
from typing import List, Optional, Union
from pydantic import BaseModel, ValidationError, Field
import asyncio
import aiofiles

class UserData(BaseModel):
    """
    Represents user-specific data.
    """
    sex: str
    age: int
    factors: Optional[List[str]] = None  # Use Optional for nullable fields

class ImageData(BaseModel):
    """
    Represents image data, including associated user data.
    """
    image_name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    user_data: Optional[UserData] = None # Nested Pydantic model

# This will store all our ImageData objects loaded from the file
# We use a list to store multiple image data entries

class ImageDatabase():
    # Define the data file name
    DATA_FILE = "database.json"
    _all_image_data: List[ImageData] = []

    def __init__(self):
        """
        The constructor (initializer) for the ImageDatabase class.

        It's called automatically when a new Image Database is created.
        """
        self.load_data_from_file() # Load data when the program starts


    def _initialize_data_file(self):
        """
        Ensures the data.json file exists and is initialized as an empty JSON array
        if it's empty or doesn't exist.
        """
        if not os.path.exists(self.DATA_FILE) or os.path.getsize(self.DATA_FILE) == 0:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4) # Write an empty JSON array

    def load_data_from_file(self):
        """
        Loads ImageData objects from the data.json file.
        Updates the global _all_image_data list.
        """
        #global _all_image_data
        self._initialize_data_file() # Ensure file exists and is initialized

        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                raw_data = f.read()
                if not raw_data.strip(): # Handle truly empty file after init
                    self._all_image_data = []
                    return

                # Pydantic v2 uses model_validate_json for parsing from JSON string
                # Pydantic v1 used parse_raw_as
                # To handle a list of objects, we use List[ImageData] as the type
                self._all_image_data = [ImageData.model_validate(item) for item in json.loads(raw_data)]

            print(f"Successfully loaded {len(self._all_image_data)} image data entries from {self.DATA_FILE}")
        except (json.JSONDecodeError, FileNotFoundError, ValidationError) as e:
            print(f"Error loading data from {DATA_FILE}: {e}")
            print("Initializing with an empty data set.")
            self._all_image_data = []
            self._initialize_data_file() # Re-initialize if corruption occurred

    async def save_data_to_file(self):
        """
        Saves the current _all_image_data (list of ImageData objects)
        to the data.json file.
        """
        try:
            # Pydantic v2 uses model_dump for converting to dict for JSON serialization
            # Convert list of Pydantic models to list of dictionaries
            data_to_save = [item.model_dump(mode='json') for item in self._all_image_data]
            
            #with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            #    json.dump(data_to_save, f, indent=4, ensure_ascii=False)

            async with aiofiles.open(self.DATA_FILE, "w") as f:
                await f.write(json.dumps(data_to_save, indent=4))


            print(f"Successfully saved {len(self._all_image_data)} image data entries to {self.DATA_FILE}")
        except Exception as e:
            print(f"Error saving data to {self.DATA_FILE}: {e}")

    async def add_image_data(self, new_image_entry: ImageData):
        """
        Adds a new ImageData object to the in-memory list and saves to file.
        """
        #global _all_image_data
        self._all_image_data.append(new_image_entry)
        await self.save_data_to_file()

    def get_all_image_data(self) -> List[ImageData]:
        """
        Returns the current list of all ImageData objects.
        """
        return self._all_image_data

    def find_image_data_by_name(self, image_name: str) -> Optional[ImageData]:
        """
        Finds an ImageData object by its image_name.
        """
        for item in self._all_image_data:
            if item.image_name == image_name:
                return item
        return None


######## TESTING

def avoidDoubles(database):
    if not database.find_image_data_by_name(image1.image_name):
        print(f"\nAdding new image data for {image1.image_name}...")
        database.add_image_data(image1)
    else:
        print(f"\nImage data for {image1.image_name} already exists.")

    if not database.find_image_data_by_name(image2.image_name):
        print(f"Adding new image data for {image2.image_name}...")
        database.add_image_data(image2)
    else:
        print(f"Image data for {image2.image_name} already exists.")

    if not database.find_image_data_by_name(image3.image_name):
        print(f"Adding new image data for {image3.image_name}...")
        database.add_image_data(image3)
    else:
        print(f"Image data for {image3.image_name} already exists.")


def searchData(database):
    print("\n--- Current Data in Storage ---")
    current_data = database.get_all_image_data()
    for idx, img_data in enumerate(current_data):
        print(f"Entry {idx + 1}:")
        print(f"  Image Name: {img_data.image_name}")
        print(f"  Description: {img_data.description}")
        print(f"  Tags: {img_data.tags}")
        if img_data.user_data:
            print(f"  User Data: Sex={img_data.user_data.sex}, Age={img_data.user_data.age}, Factors={img_data.user_data.factors}")
        else:
            print("  User Data: None")
        print("-" * 20)

    # 5. Find a specific entry
    print("\n--- Finding a specific entry ---")
    found_image = database.find_image_data_by_name("photo_1.jpg")
    if found_image:
        print(f"Found 'photo_1.jpg': Description='{found_image.description}', User Age={found_image.user_data.age if found_image.user_data else 'N/A'}")
    else:
        print("photo_1.jpg not found.")

    found_image_missing_user = database.find_image_data_by_name("flower.jpeg")
    if found_image_missing_user:
        print(f"Found 'flower.jpeg': User Data is None? {found_image_missing_user.user_data is None}")


# --- Program Start ---
if __name__ == "__main__":
    print("Program started. Loading data...")
    database = ImageDatabase()

    # --- Example Usage ---

    # # 1. Create new UserData objects
    # user1 = UserData(sex="male", age=30, factors=["active", "healthy"])
    # user2 = UserData(sex="female", age=25) # factors is optional

    # # 2. Create new ImageData objects
    # image1 = ImageData(
    #     image_name="photo_1.jpg",
    #     description="A beautiful sunset",
    #     tags=["nature", "sunset", "sky"],
    #     user_data=user1
    # )

    # image2 = ImageData(
    #     image_name="document_scan.png",
    #     description="Scan of an old document",
    #     tags=["document", "historical"],
    #     user_data=user2
    # )

    # image3 = ImageData(
    #     image_name="flower.jpeg",
    #     description="A vibrant flower in bloom",
    #     tags=["flower", "garden"],
    #     # user_data is optional, so we can omit it
    # )

    #asyncio.run(database.add_image_data(image1))
    # database.add_image_data(image2)
    # database.add_image_data(image3)
    
    # 3. Add new data if it's not already present (to avoid duplicates on re-run)
    #avoidDoubles(database)

    # 4. Retrieve and display all current data
    #searchData(database)

    # You can manually inspect 'data.json' after running this script to see the stored data.
import json
from pydantic import BaseModel, Field, ValidationError
from typing import Tuple, Literal, List

class GraphicalObject(BaseModel):
    """
    Represents a graphical object with an ID, type, position, and size.
    """
    id: int = Field(..., description="Unique identifier for the graphical object")
    
    object_type: Literal["Circle", "Rectangle", "Image", "Text"] = Field(
        ..., 
        description="Type of the graphical object (Circle, Rectangle, Image, or Text)"
    )
    
    position: Tuple[int, int] = Field(..., description="Position of the object as an (x, y) tuple")
    size_x: int = Field(..., gt=0, description="Size of the object in the x-direction (width)")
    size_y: int = Field(..., gt=0, description="Size of the object in the y-direction (height)")

    # --- Getter Methods ---
    def get_id(self) -> int:
        """Returns the ID of the graphical object."""
        return self.id

    def get_object_type(self) -> Literal["Circle", "Rectangle", "Image", "Text"]:
        """Returns the type of the graphical object."""
        return self.object_type

    def get_position(self) -> Tuple[int, int]:
        """Returns the position (x, y) of the graphical object."""
        return self.position

    def get_size_x(self) -> int:
        """Returns the size in the x-direction (width) of the graphical object."""
        return self.size_x

    def get_size_y(self) -> int:
        """Returns the size in the y-direction (height) of the graphical object."""
        return self.size_y

    # --- Setter Methods ---
    def set_id(self, new_id: int):
        """Sets the ID of the graphical object."""
        # Pydantic's validation is usually done on initialization.
        # For setters, we manually re-validate the individual field if necessary.
        # Here, we trust the type hint and direct assignment.
        if not isinstance(new_id, int):
            raise TypeError("ID must be an integer.")
        self.id = new_id

    def set_object_type(self, new_type: Literal["Circle", "Rectangle", "Image", "Text"]):
        """Sets the type of the graphical object, with validation."""
        # Leveraging Pydantic's validation by temporarily creating a model just for this field
        try:
            # Create a temporary model to validate just the object_type field
            class TempModel(BaseModel):
                temp_type: Literal["Circle", "Rectangle", "Image", "Text"]
            TempModel(temp_type=new_type) # This will raise ValidationError if new_type is invalid
            self.object_type = new_type
        except ValidationError as e:
            raise ValueError(f"Invalid object type: {e}") from e

    def set_position(self, new_position: Tuple[int, int]):
        """Sets the position (x, y) of the graphical object, with validation."""
        try:
            # Create a temporary model to validate just the position field
            class TempModel(BaseModel):
                temp_pos: Tuple[int, int]
            TempModel(temp_pos=new_position) # This will raise ValidationError if new_position is invalid
            self.position = new_position
        except ValidationError as e:
            raise ValueError(f"Invalid position: {e}") from e

    def set_size_x(self, new_size_x: int):
        """Sets the size in the x-direction (width) of the graphical object, with validation."""
        try:
            # Create a temporary model to validate just the size_x field
            class TempModel(BaseModel):
                temp_size_x: int = Field(..., gt=0)
            TempModel(temp_size_x=new_size_x) # This will raise ValidationError if new_size_x is invalid
            self.size_x = new_size_x
        except ValidationError as e:
            raise ValueError(f"Invalid size_x: {e}") from e

    def set_size_y(self, new_size_y: int):
        """Sets the size in the y-direction (height) of the graphical object, with validation."""
        try:
            # Create a temporary model to validate just the size_y field
            class TempModel(BaseModel):
                temp_size_y: int = Field(..., gt=0)
            TempModel(temp_size_y=new_size_y) # This will raise ValidationError if new_size_y is invalid
            self.size_y = new_size_y
        except ValidationError as e:
            raise ValueError(f"Invalid size_y: {e}") from e


class GraphicalObjectList(BaseModel):
    objects: List[GraphicalObject] = []

#################################################
# convert model to json
def _modelToJson(data):
    return (json.loads(data.model_dump_json()))

# saving the data
def _saveData(fname, data):
    with open(fname, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# loading the data
def _loadData(fname) -> dict:
    with open(fname) as f:
        file_content = f.read()
        result = json.loads(file_content)

    if (isinstance(result, str)):
        return json.loads(result)
    else:
        return result

# get printable string 
def getDataString(data: GraphicalObjectList):
    result = ""
    for object in data.objects:
        result += f"{object.get_id()}, "
        result += f"{object.get_object_type()}, "
        result += f"{object.get_size_x()}, "
        result += f"{object.get_size_y()}, "
        result += f"{object.get_position()}" + "\n"
    return result

# save GraphicalObjectList to file
def saveObjectList(fname, data: GraphicalObjectList):
    model = _modelToJson(data)
    _saveData(fname, model)

# load GraphicalObjectList from json file
def loadObjectList(fname):
    data = _loadData(fname)
    result = GraphicalObjectList.model_validate(data)
    return result

#### TESTING ####

def testing():
    # Create valid GraphicalObjects
    obj1 = GraphicalObject(
        id=1,
        object_type="Rectangle",
        position=(100, 200),
        size_x=50,
        size_y=75
    )
    print("Successfully created obj1:")
    obj2 = GraphicalObject(
        id=2,
        object_type="Circle",
        position=(50, 50),
        size_x=30,
        size_y=30
    )
    print("\nSuccessfully created obj2:")

    objectlist = GraphicalObjectList(objects=[obj1, obj2])
    saveObjectList("objects.json", objectlist)
    print (getDataString(objectlist))

    objectlist = loadObjectList("objects_erweitert.json")
    objectlist.objects[0].set_size_x(2000)
    saveObjectList("objects.json", objectlist)

    print (getDataString(objectlist))


if __name__ == "__main__":
    testing()


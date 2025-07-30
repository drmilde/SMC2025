from pydantic import BaseModel, Field
from typing import Tuple, Literal

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

# Example usage:
if __name__ == "__main__":
    try:
        # Create valid GraphicalObjects
        obj1 = GraphicalObject(
            id=1,
            object_type="Rectangle",
            position=(100, 200),
            size_x=50,
            size_y=75
        )
        print("Successfully created obj1:")
        print(obj1.model_dump_json(indent=2))

        obj2 = GraphicalObject(
            id=2,
            object_type="Circle",
            position=(50, 50),
            size_x=30,
            size_y=30
        )
        print("\nSuccessfully created obj2:")
        print(obj2.model_dump_json(indent=2))
        
        obj3 = GraphicalObject(
            id=3,
            object_type="Image",
            position=(0, 0),
            size_x=640,
            size_y=480
        )
        print("\nSuccessfully created obj3:")
        print(obj3.model_dump_json(indent=2))

        # Example of validation error (invalid object_type)
        print("\nAttempting to create an invalid object (invalid type):")
        try:
            invalid_obj_type = GraphicalObject(
                id=4,
                object_type="Triangle", # This will cause an error
                position=(10, 10),
                size_x=20,
                size_y=20
            )
        except Exception as e:
            print(f"Validation error caught: {e}")

        # Example of validation error (size_x must be greater than 0)
        print("\nAttempting to create an invalid object (size_x = 0):")
        try:
            invalid_obj_size = GraphicalObject(
                id=5,
                object_type="Text",
                position=(10, 10),
                size_x=0,
                size_y=20
            )
        except Exception as e:
            print(f"Validation error caught: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
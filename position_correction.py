import os
from PIL import Image

# Directory where the RG images are stored
input_dir = "data/RG_Aberto"

def correct_orientation(image_path):
    """Checks and corrects the image orientation to vertical."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            if width > height:  # If the image is in landscape mode
                print(f"↻ Rotating {image_path} to the correct position...")
                img = img.rotate(-90, expand=True)  # Rotates 90° counterclockwise
                img.save(image_path)  # Overwrites the corrected image
                print(f"✅ Correction applied: {image_path}")
            else:
                print(f"✔ {image_path} is already in the correct position.")
    
    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")

if __name__ == "__main__":
    if not os.path.exists(input_dir):
        print(f"❌ The directory '{input_dir}' was not found.")
    else:
        print(f"📂 Checking images in '{input_dir}'...")
        
        for file_name in os.listdir(input_dir):
            if file_name.lower().endswith((".jpg", ".jpeg", ".png")):  # Filters only images
                image_path = os.path.join(input_dir, file_name)
                correct_orientation(image_path)
        
        print("✅ All images have been checked and corrected (if necessary).")


import os
import sys

try:
    from PIL import Image
except ImportError:
    print("PIL not installed")
    sys.exit(1)

start_dir = '/home/codiac/Desktop/Projects/Python/SPACE-SHOOTER/Sprites'
base_dir = '/home/codiac/Desktop/Projects/Python/SPACE-SHOOTER'

img_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

images = []

for root, dirs, files in os.walk(start_dir):
    for f in files:
        if os.path.splitext(f)[1].lower() in img_extensions:
            full_path = os.path.join(root, f)
            try:
                with Image.open(full_path) as img:
                    width, height = img.size
                    rel_path = os.path.relpath(full_path, base_dir)
                    images.append((rel_path, width, height))
            except Exception as e:
                pass

# Sort for consistent output
images.sort()

with open('sprites_list.txt', 'w') as f:
    for path, w, h in images:
        f.write(f"{path} {w} {h}\n")

import os
import subprocess
import json
import time
with open('last_compress.json', 'r') as f:
    last_compress = json.load(f)
def check_svg_installed():
    """Check if svgo is installed."""
    try:
        subprocess.run(['svgo', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def compress_svg(dir: str = 'data/font'):
    """Compress SVG files in the given directory using svgo.
    @param dir: Directory to search for SVG files."""

    if not check_svg_installed():
        print("svgo is not installed. Please install it to use this function.")
        print("Run 'npm install -g svgo' to install svgo.")
        return

    # get current time
    current_time = time.time()
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith('.svg'):
                # Check if the file was modified after the last compression
                svg_file = os.path.join(root, file)
                if svg_file in last_compress:
                    last_modified_time = os.path.getmtime(svg_file)
                    if last_modified_time <= last_compress[svg_file]:
                        continue
                try:
                    subprocess.run(['svgo', svg_file, "-o", svg_file], check=True)
                    print(f"Compressed: {svg_file}")
                    last_compress[svg_file] = current_time  # Update the last compression time
                    # Update the last compression time
                except subprocess.CalledProcessError as e:
                    print(f"Error compressing {svg_file}: {e}")

    # Save the last compression time to a file
    with open('last_compress.json', 'w') as f:
        json.dump(last_compress, f)

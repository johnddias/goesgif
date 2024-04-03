import os
import sys
import argparse
from datetime import datetime, timedelta
from wand.image import Image as WandImage
import re
import progressbar

def find_images(time_threshold, input_dir):
    time_threshold_date = datetime.utcnow() - timedelta(hours=time_threshold)
    files = []
    for root, _, filenames in os.walk(input_dir):
        for filename in filenames:
            if filename.startswith("GOES") and len(filename) > 5 and filename[4:6].isdigit():
                match = re.search(r"_(\d{8}T\d{6}Z)\.jpg$", filename)
                if match:
                    time_part = datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ")
                    if time_part > time_threshold_date:
                        files.append((os.path.join(root, filename), time_part))
    # Sort files by timestamp (oldest to newest)
    files.sort(key=lambda x: x[1])
    return [f[0] for f in files]

def create_gifs(files, output_dir, resize_percentage, region, channels, include_enhanced, convert_delay, convert_loop):
    widgets = [progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    bar = progressbar.ProgressBar(widgets=widgets, maxval=len(files))
    bar.start()
    for i, file_path in enumerate(files):
        filename = os.path.basename(file_path)
        parts = filename.split("_")
        img_region = parts[1]
        img_channel = parts[2] + ("_enhanced" if len(parts) > 3 and parts[3] == "enhanced" else "")
        if region == 'all' or region == img_region:
            if channels == 'all' or any([ch in img_channel for ch in channels.split(',')]):
                output_folder = os.path.join(output_dir, img_region, img_channel)
                os.makedirs(output_folder, exist_ok=True)
                output_file = os.path.join(output_folder, f"output_{img_region}_{img_channel}.gif")
                if '_enhanced' in img_channel and not include_enhanced:
                    continue  # Skip processing enhanced channels if not specified
                with WandImage(filename=file_path) as img:
                    # Resize the image
                    img.resize(int(img.width * (resize_percentage / 100)), int(img.height * (resize_percentage / 100)))
                    # Save the resized image
                    resized_file_path = os.path.join(output_folder, filename)
                    img.save(filename=resized_file_path)
                    # Convert the resized image to GIF and append to the existing GIF if it exists
                    if os.path.exists(output_file):
                        with WandImage(filename=output_file) as existing_gif:
                            existing_gif.sequence.append(img)
                            existing_gif.save(filename=output_file)
                    else:
                        with WandImage() as new_gif:
                            new_gif.sequence.append(img)
                            new_gif.save(filename=output_file)
                    # Remove the resized image file
                    os.remove(resized_file_path)
        bar.update(i+1)
    bar.finish

def main():
    parser = argparse.ArgumentParser(description='Create GIFs from images.')
    parser.add_argument('input_dir', type=str, help='Input directory containing images')
    parser.add_argument('output_dir', type=str, help='Output directory for GIFs')
    parser.add_argument('--time_threshold', type=int, default=24, help='Time threshold in hours (default: 24)')
    parser.add_argument('--resize_percentage', type=int, default=25, help='Resize percentage (default: 25)')
    parser.add_argument('--region', type=str, default='all', help='Region to process (FD, M1, M2)')
    parser.add_argument('--channels', type=str, default='all', help='Channels to process (comma-separated list)')
    parser.add_argument('--include_enhanced', action='store_true', help='Include enhanced channels')
    parser.add_argument('--convert_delay', type=int, default=100, help='Delay between frames in the GIF (default: 100)')
    parser.add_argument('--convert_loop', type=int, default=0, help='Number of times the GIF should loop (default: 0, loop indefinitely)')
    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' not found.")
        sys.exit(1)

    print("Finding images...")
    files = find_images(args.time_threshold, args.input_dir)
    print(f"Found {len(files)} images.")

    if len(files) == 0:
        print("No images found. Exiting.")
        sys.exit(0)

    print("Creating GIFs...")
    create_gifs(files, args.output_dir, args.resize_percentage, args.region, args.channels, args.include_enhanced,
                args.convert_delay, args.convert_loop)

    print(f"GIFs created in {args.output_dir} with resize percentage {args.resize_percentage}%")

if __name__ == "__main__":
    main()

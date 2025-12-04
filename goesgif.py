import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
try:
    from zoneinfo import ZoneInfoNotFoundError
except ImportError:
    from zoneinfo._common import ZoneInfoNotFoundError
from wand.image import Image as WandImage
from wand.drawing import Drawing
from wand.color import Color
import re
from tqdm import tqdm
from collections import defaultdict

def find_images(time_threshold, input_dir, allowed_satellites):
    time_threshold_date = datetime.now(timezone.utc) - timedelta(hours=time_threshold)
    files = []
    for root, _, filenames in os.walk(input_dir):
        for filename in filenames:
            if filename.startswith("GOES") and len(filename) > 5 and filename[4:6].isdigit():
                match = re.search(r"_(\d{8}T\d{6}Z)\.jpg$", filename)
                if match:
                    satellite = filename.split("_")[0]
                    if allowed_satellites != 'all' and satellite not in allowed_satellites.split(','):
                        continue
                    time_part = datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
                    if time_part > time_threshold_date:
                        files.append((os.path.join(root, filename), time_part, satellite))
    files.sort(key=lambda x: x[1])
    return files

def draw_timestamp(img, timestamp, tz_label, timestamp_scale_factor=1.0):
    timestamp_str = timestamp.strftime(f"%Y-%m-%d %H:%M {tz_label}")
    with Drawing() as draw:
        # Scale font size based on image height and user-defined scale factor
        # Base size is 1.5% of image height, with minimum of 12px
        base_font_size = int(img.height * 0.015 * timestamp_scale_factor)
        font_size = max(12, base_font_size)
        draw.font_size = font_size
        draw.fill_color = Color("white")
        draw.stroke_color = Color("black")
        draw.text_antialias = True
        # Scale position based on image dimensions
        margin_x = max(5, int(img.width * 0.005))
        margin_y = max(5, int(img.height * 0.005))
        draw.text(margin_x, img.height - margin_y, timestamp_str)
        draw(img)

def crop_gulf_closeup(img):
    """
    Crop the Gulf of Mexico and Southeast US region from a GOES full disk image.
    This region includes the Gulf of Mexico, Florida, and the Southeast US coast.
    
    Args:
        img: Wand Image object (full disk image)
    
    Returns:
        Wand Image object (cropped closeup)
    """
    width = img.width
    height = img.height
    
    # Define crop region as percentages of full disk image
    # For GOES full disk images, the Gulf of Mexico region is typically in the
    # upper-left to upper-center area (west/north of center):
    # - Left edge: ~25% (starts from west, capturing Gulf region)
    # - Top edge: ~10% (starts from north, capturing full Southeast US including TN, SC, NC, AR)
    # - Width: ~35% (extends east to cover Florida and Atlantic coast)
    # - Height: ~35% (extends south to cover full Gulf region while including northern states)
    left = int(width * 0.25)
    top = int(height * 0.10)
    crop_width = int(width * 0.35)
    crop_height = int(height * 0.35)
    
    # Ensure we don't exceed image bounds
    crop_width = min(crop_width, width - left)
    crop_height = min(crop_height, height - top)
    
    # Crop the image
    img.crop(left=left, top=top, width=crop_width, height=crop_height)
    return img

def create_gifs(files, output_dir, resize_percentage, region, channels,
                include_enhanced, convert_delay, convert_loop, log_file, user_timezone, closeup=False, closeup_resize_percentage=None, timestamp_scale_factor=1.0):
    grouped = defaultdict(list)
    log = open(log_file, 'w', encoding='utf-8') if log_file else None

    try:
        tz = ZoneInfo(user_timezone)
    except ZoneInfoNotFoundError:
        print(f"Error: Timezone '{user_timezone}' not found.")
        print("This may be because the 'tzdata' package is not installed.")
        print("Install it with: pip install tzdata")
        print("Common timezone examples: UTC, America/New_York, America/Chicago, Europe/London")
        sys.exit(1)
    tz_label = tz.key.split("/")[-1].replace("_", " ")

    for file_path, timestamp, satellite in files:
        filename = os.path.basename(file_path)
        parts = filename.split("_")
        img_region = parts[1]
        img_channel = parts[2] + ("_enhanced" if len(parts) > 3 and parts[3] == "enhanced" else "")

        if region != 'all' and region != img_region:
            continue
        if channels != 'all' and not any([ch in img_channel for ch in channels.split(',')]):
            continue
        if '_enhanced' in img_channel and not include_enhanced:
            continue

        key = (satellite, img_region, img_channel)
        grouped[key].append((file_path, timestamp))

    total_files = sum(len(g) for g in grouped.values())
    bar = tqdm(total=total_files, unit='file', desc='Processing')
    count = 0

    for (satellite, img_region, img_channel), group in grouped.items():
        # Determine if we should apply closeup cropping
        apply_closeup = closeup and img_region == 'FD'
        
        # Create appropriate output folder and filename
        if apply_closeup:
            output_folder = os.path.join(output_dir, satellite, img_region, img_channel, 'closeup')
            output_file = os.path.join(output_folder, f"output_{satellite}_{img_region}_{img_channel}_closeup.gif")
        else:
            output_folder = os.path.join(output_dir, satellite, img_region, img_channel)
            output_file = os.path.join(output_folder, f"output_{satellite}_{img_region}_{img_channel}.gif")
        
        os.makedirs(output_folder, exist_ok=True)

        last_time = None
        gif = None

        for file_path, timestamp in group:
            with WandImage(filename=file_path) as img:
                # Apply closeup crop if enabled and this is a full disk image
                if apply_closeup:
                    crop_gulf_closeup(img)
                    # Use closeup-specific resize percentage if provided, otherwise use default
                    actual_resize = closeup_resize_percentage if closeup_resize_percentage is not None else resize_percentage
                else:
                    actual_resize = resize_percentage
                
                img.resize(
                    int(img.width * (actual_resize / 100)),
                    int(img.height * (actual_resize / 100))
                )
                # Ensure timestamp is timezone-aware before conversion
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                local_time = timestamp.astimezone(tz)
                draw_timestamp(img, local_time, tz_label, timestamp_scale_factor)
                img.delay = convert_delay // 10
                
                # Stream frame directly to GIF instead of collecting in memory
                if gif is None:
                    gif = WandImage()
                    gif.sequence.append(img.clone())
                else:
                    gif.sequence.append(img.clone())

            if log:
                log.write(f"{file_path} -> {output_file}\n")
                if last_time:
                    gap = (timestamp - last_time).total_seconds()
                    # GOES images are typically 30 minutes apart, so only warn about gaps > 45 minutes
                    if gap > 2700:  # 45 minutes in seconds
                        log.write(f"  ⚠ Gap detected: {gap/60:.1f} min between frames\n")
                last_time = timestamp

            count += 1
            bar.update(1)

        if gif is not None:
            # Set delay and optimization after all frames are added
            for frame in gif.sequence:
                frame.delay = convert_delay // 10
            gif.type = 'optimize'
            gif.loop = convert_loop
            gif.save(filename=output_file)
            gif.close()

    bar.close()
    if log:
        log.close()

def main():
    parser = argparse.ArgumentParser(description='Create GIFs from GOES satellite images.')
    parser.add_argument('input_dir', type=str, help='Input directory containing images')
    parser.add_argument('output_dir', type=str, help='Output directory for GIFs')
    parser.add_argument('--time_threshold', type=int, default=24, help='Time threshold in hours (default: 24)')
    parser.add_argument('--resize_percentage', type=int, default=25, help='Resize percentage (default: 25)')
    parser.add_argument('--region', type=str, default='all', help='Region to process (FD, M1, M2)')
    parser.add_argument('--channels', type=str, default='all', help='Channels to process (comma-separated list)')
    parser.add_argument('--include_enhanced', action='store_true', help='Include enhanced channels')
    parser.add_argument('--convert_delay', type=int, default=100, help='Delay between frames in the GIF (default: 100ms)')
    parser.add_argument('--convert_loop', type=int, default=0, help='Number of times the GIF should loop (0 = infinite)')
    parser.add_argument('--log_file', type=str, default=None, help='Path to log file listing included images and gaps')
    parser.add_argument('--satellites', type=str, default='all', help='Comma-separated list of satellites to include (e.g., GOES18,GOES19)')
    parser.add_argument('--timezone', type=str, default='UTC', help='Timezone for timestamp overlay (default: UTC)')
    parser.add_argument('--closeup', action='store_true', help='Create closeup GIFs of Gulf/Southeast US region from full disk images')
    parser.add_argument('--closeup_resize_percentage', type=int, default=None, help='Resize percentage for closeup GIFs (default: uses --resize_percentage)')
    parser.add_argument('--timestamp_scale_factor', type=float, default=1.0, help='Scale factor for timestamp font size (default: 1.0, range: 0.5-3.0 recommended)')

    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' not found.")
        sys.exit(1)

    print("Finding images...")
    files = find_images(args.time_threshold, args.input_dir, args.satellites)
    print(f"Found {len(files)} images.")

    if len(files) == 0:
        print("No images found. Exiting.")
        sys.exit(0)

    print("Creating GIFs...")
    create_gifs(files, args.output_dir, args.resize_percentage, args.region, args.channels,
                args.include_enhanced, args.convert_delay, args.convert_loop, args.log_file, args.timezone, args.closeup, args.closeup_resize_percentage, args.timestamp_scale_factor)

    print(f"GIFs created in {args.output_dir} with resize percentage {args.resize_percentage}%")
    if args.log_file:
        print(f"Log written to {args.log_file}")

if __name__ == "__main__":
    main()

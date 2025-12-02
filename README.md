# GOES Image GIF Generator

This script processes GOES satellite `.jpg` images and generates animated GIFs grouped by satellite, region, and channel. It supports filtering by satellite, time range, and channel; resizing images; detecting time gaps between frames; and overlaying timestamps on each frame.

## Features

- Supports multiple GOES satellites (GOES16, GOES18, GOES19, etc.)
- Recursively finds GOES image files modified within the last N hours
- Filters by satellite, region, channel, and enhancement
- Resizes images before GIF creation
- **Create closeup GIFs of Gulf/Southeast US region from full disk images**
- Logs processed images and detects time gaps in sequence
- Adds timestamp overlays to each frame
- Timezone-aware timestamp formatting
- Organizes GIFs by satellite/region/channel
- Progress bar during processing

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Make sure [ImageMagick](https://imagemagick.org) is installed and accessible (required by `wand`).

## Usage

```bash
python goesgif.py INPUT_DIR OUTPUT_DIR [options]
```

### Required Arguments

- `INPUT_DIR`: Path to the directory containing GOES `.jpg` images
- `OUTPUT_DIR`: Directory where the output GIFs will be saved

### Options

| Option | Description |
|--------|-------------|
| `--time_threshold HOURS` | Look for images modified within the past N hours (default: 24) |
| `--resize_percentage PERCENT` | Resize image by percentage before generating GIF (default: 25) |
| `--region REGION` | Region to process: `FD`, `M1`, `M2`, or `all` (default: all) |
| `--channels CH1,CH2,...` | Comma-separated list of channels (e.g., `CH13,CH02`) or `all` |
| `--satellites SAT1,SAT2,...` | Comma-separated list of satellites to include (e.g., `GOES18,GOES19`) or `all` |
| `--include_enhanced` | Include images with `_enhanced` in channel name |
| `--closeup` | Create closeup GIFs of Gulf/Southeast US region from full disk images (FD only) |
| `--convert_delay MS` | Frame delay in milliseconds (default: 100) |
| `--convert_loop N` | Number of times the GIF should loop (`0` = infinite) |
| `--log_file FILE` | Log file to write list of included images and detected time gaps |
| `--timezone ZONE` | Timezone for timestamp overlay (default: `UTC`, e.g., `America/Chicago`) |

### Example

```bash
python goesgif.py ./images ./gifs \
  --time_threshold 36 \
  --resize_percentage 50 \
  --region FD \
  --channels CH13 \
  --satellites GOES19 \
  --include_enhanced \
  --log_file goesgif.log \
  --timezone America/Chicago
```

This will create a GIF for `GOES19` Full Disk `CH13` images (including enhanced versions) within the last 36 hours, resize them to 50%, and overlay timestamps in the Central Time zone.

### Closeup Example

```bash
python goesgif.py ./images ./gifs \
  --time_threshold 36 \
  --resize_percentage 75 \
  --region FD \
  --channels CH13 \
  --satellites GOES19 \
  --closeup \
  --timezone America/Chicago
```

This will create a closeup GIF of the Gulf of Mexico and Southeast US region from full disk images. Closeup GIFs are saved in a `closeup` subdirectory and include `_closeup` in the filename.

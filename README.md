# GOES GIF Creator

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

Create animated GIFs from GOES satellite images: visualize weather events, cloud motion, and more.

## Overview

GOES GIF Creator helps you turn batches of [GOES](https://www.goes.noaa.gov/) (Geostationary Operational Environmental Satellites) images into time-lapse GIFs. Useful for meteorologists, enthusiasts, researchers, and educators who want a quick way to visualize satellite data.

## Features

- Select region (FD, M1, M2)
- Filter by channels (e.g., CH07, CH13)
- Resize images and set delay/loop for GIFs
- Optional: Include enhanced channels
- Fast batch processing

## Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/installation/)
- GOES satellite image files (supported formats: PNG, JPEG)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/johnddias/goesgif.git
   cd goesgif
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python goesgif.py <input_dir> <output_dir> [--options]
```

### Options

- `--time_threshold` &nbsp; Time threshold in hours (default: 24)
- `--resize_percentage` &nbsp; Resize percentage (default: 25)
- `--region` &nbsp; Region to process (`FD`, `M1`, `M2`)
- `--channels` &nbsp; Comma-separated channels (default: all)
- `--include_enhanced` &nbsp; Include enhanced channels
- `--convert_delay` &nbsp; Delay between frames in the GIF (default: 100 ms)
- `--convert_loop` &nbsp; Number of times the GIF should loop (default: 0, infinite)

### Example

```bash
python goesgif.py /path/to/input_images /path/to/output_gifs --region FD --channels CH07,CH13 --include_enhanced
```

### Sample Output

- `/path/to/output_gifs/FD_CH07_CH13.gif`

## Troubleshooting

- **Missing dependencies?**  
  Re-run `pip install -r requirements.txt`.
- **No images processed?**  
  Check that your input directory contains supported image files and correct region/channel options.

## Contributing

Pull requests, feature suggestions, and bug reports are welcome!  
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Licensed under the [Apache 2.0 License](LICENSE).
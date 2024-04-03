# GOES GIF Creator

This script creates animated GIFs from GOES satellite images.

## Installation

1. Clone the repository:
```
git clone https://github.com/your-username/goesgif.git
```
2. Install the required Python packages:
```
pip install -r requirements.txt
```
# Usage

Run the script with the following command:
```
python goesgif.py <input_dir> <output_dir> [--options]
```

# Options

    --time_threshold: Time threshold in hours (default: 24)
    --resize_percentage: Resize percentage (default: 25)
    --region: Region to process (FD, M1, M2)
    --channels: Channels to process (comma-separated list, default is all channels)
    --include_enhanced: Include enhanced channels
    --convert_delay: Delay between frames in the GIF (default: 100)
    --convert_loop: Number of times the GIF should loop (default: 0, loop indefinitely)

# Example
```
python goesgif.py /path/to/input_images /path/to/output_gifs --region FD --channels CH07,CH13 --include_enhanced
```
# License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.




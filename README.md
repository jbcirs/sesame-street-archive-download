# Sesame Street Archive Downloader

A Python script to download all Sesame Street episodes from the Internet Archive. This tool downloads the `.ia.mp4` format files from the `sesame-street_202308` collection on archive.org.

## Features

- **Parallel Downloads**: Uses multiple threads (4 by default) for faster downloading
- **Resume Support**: Automatically resumes interrupted downloads
- **Progress Tracking**: Shows download progress with percentage and transfer rates
- **Error Handling**: Retries failed downloads with exponential backoff
- **Duplicate Detection**: Skips files that are already completely downloaded
- **URL Decoding**: Saves files with properly decoded, readable filenames

## Requirements

- Python 3.6 or higher
- Internet connection
- Sufficient disk space (episodes are typically 100-200MB each)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/jbcirs/sesame-street-archive-download.git
   cd sesame-street-archive-download
   ```

2. No additional dependencies required - uses only Python standard library.

## Usage

Run the script:

```bash
python download.py
```

Or on some systems:

```bash
python3 download.py
```

### What it does

1. **Scans** the Internet Archive for all `.ia.mp4` files
2. **Lists** all found episodes with their filenames
3. **Downloads** them to a `download/` folder in the current directory
4. **Shows progress** for each download with percentage complete
5. **Skips** files that are already fully downloaded

### Example Output

```text
[INFO] Scanning index: https://archive.org/download/sesame-street_202308/
[INFO] Found 195 files:
  - Sesame Street - Episode 5008 (January 4, 2020).ia.mp4
  - Sesame Street - Episode 5009 (January 11, 2020).ia.mp4
  - ...
[INFO] Downloading to: C:\path\to\download
[DOWN] Sesame Street - Episode 5008 (January 4, 2020).ia.mp4 87818240/155432280 bytes ( 56.5%)
[OK]   Sesame Street - Episode 5008 (January 4, 2020).ia.mp4
[DONE] All tasks completed.
```

## Configuration

You can modify these settings at the top of `download.py`:

- `OUT_DIR`: Output directory (default: "download")
- `MAX_WORKERS`: Number of parallel downloads (default: 4)
- `RETRIES`: Number of retry attempts for failed downloads (default: 5)
- `TIMEOUT`: Network timeout in seconds (default: 60)

## File Organization

Downloaded files are saved in the `download/` directory with their original Internet Archive names, properly URL-decoded:

```text
download/
├── Sesame Street - Episode 5008 (January 4, 2020).ia.mp4
├── Sesame Street - Episode 5009 (January 11, 2020).ia.mp4
├── Sesame Street - Episode 5010 (January 18, 2020).ia.mp4
└── ...
```

## Notes

- The script is designed to be polite to the Internet Archive servers
- Downloads can be interrupted and resumed safely
- Files are verified for completeness after download
- The script will skip files that are already complete

## Legal Notice

This tool is for archival and educational purposes. Please respect the Internet Archive's terms of service and any applicable copyright laws. The Sesame Street content is owned by Sesame Workshop.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# YouTube Shorts Bot

A powerful automation tool for creating YouTube channels and uploading shorts videos automatically. The project consists of two main applications:
1. Account Creator - Automates YouTube channel creation
2. Video Uploader - Handles automated video uploads

## Features

- Automated Gmail login  
- YouTube channel creation
- Bulk video uploads
- Proxy support 
- CSV-based data management
- User-friendly GUI interface

## Project Structure

- `account_creator_gui.py`      # Main GUI application to create YouTube accounts
- `google_login.py`             # Helper script to log into Google
- `parsing_csv.py`              # Script to parse CSV files (emails, proxies, etc.)
- `youtube_login.py`            # Script to create a channel in YouTube
- `youtube_upload_gui.py`       # Main GUI application to upload videos
- `video_uploader.py`           # Helper script to upload videos to YouTube
- `xpaths/`                     # Directory containing the required XPaths

## Prerequisites

- Python 3.x
- Go Login Token
- Valid Gmail accounts
- Proxies (optional but recommended)
- CSV files with required data

## Installation

1. Clone the repository:
```bash 
git clone https://github.com/mohdtalal3/Youtube_shorts_bot.git
cd youtube-shorts-bot
```
2. Install required dependencies:
```bash 
pip install -r requirements.txt
```
## Usage

### 1. Account Creator Application

#### Required Input:
- Go Login Token
- CSV file with following format:
- CSV File Requirements

`Fill Name, Login_detail (like email:password:recoveryEmail), and proxy`

`Leave profile_id and account_created empty; these will be automatically populated by the script`
| Name | Login_detail | proxy | profile_id | account_created |
|------|--------------|-------|------------|-----------------|
| Talal | dftrmuykyfd50@gmail.com:AdnaN999:QhyuBlpara811807@outlook.com | 89.116.56.102:50100:kymar227:EKEPK6jNQo | | |

[Screenshot of input CSV placeholder]


#### Generates Output File : 
The application generates `output.csv` with additional fields:

| Name | Login_detail | proxy | profile_id | account_created | title | description | upload_video |
|------|--------------|-------|------------|-----------------|-------|-------------|--------------|
| Talal | dftrmuykyfd50@gmail.com:AdnaN999:QhyuBlpara811807@outlook.com | 89.116.56.102:50100:kymar227:EKEPK6jNQo | 676c6acdde240c7932849b40 | TRUE | | | |

- This output file is used in youtube upload video application.

[Screenshot of output CSV placeholder]

### 2. Video Upload Application

#### Required Input:
- Go Login Token
- Output CSV from Account Creator
- Video file(s)

#### Steps:
1. Launch `youtube_upload_gui.py`
2. Enter Go Login token
3. Select the output CSV from Account Creator
4. Fill in title and description for videos
5. Select video file(s)
6. Run the application

#### Output:
The application generates `upload_data.csv` with upload status:

| Name | Login_detail | proxy | profile_id | account_created | title | description | upload_video |
|------|--------------|-------|------------|-----------------|-------|-------------|--------------|
| Talal | dftrmuykyfd50@gmail.com:AdnaN999:QhyuBlpara811807@outlook.com | 89.116.56.102:50100:kymar227:EKEPK6jNQo | 676c6acdde240c7932849b40 | TRUE | My Video | Video Description | TRUE |

[Screenshot of upload data CSV placeholder]

## GUI Screenshots

[Account Creator GUI Screenshot placeholder]

[Video Uploader GUI Screenshot placeholder]

## Important Notes

1. **CSV Format**:
  - For Account Creator: Only fill Name, Login_detail, and proxy
  - Profile_id and account_created are auto-populated
  - For Video Uploader: Fill title and description fields
  - upload_video field is auto-populated after successful upload

2. **Login Details Format**:
  - Format: `email:password:recovery_email`  
  - Example: `dftrmuykyfd50@gmail.com:AdnaN999:QhyuBlpara811807@outlook.com`

3. **Proxy Format**:
  - Format: `ip:port:username:password`
  - Example: `89.116.56.102:50100:kymar227:EKEPK6jNQo`

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please create an issue in the GitHub repository or contact [your contact information].
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-06
### Official Release
- **Stability Improvements**: Optimized performance and fixed minor bugs from the beta release.
- **Enhanced User Interface**: Refined CLI messages for better user guidance and error handling.
- **Download Complete Confirmation**: Added "Download complete!" and "Thank you for using" message after successful downloads only.
- **Changelog Display on Update**: Displays the changelog for new updates, ensuring users are informed of new features and improvements before downloading.

## [1.0.0-beta] - 2024-11-05
### Initial Beta Release
- **Platform Support**: Added download capabilities for popular platforms:
  - **YouTube**: Download videos with format selection and audio merging.
  - **Facebook**: Scrape and download videos.
  - **Instagram**: Download individual posts, including photos and videos.
  - **TikTok**: Download videos with format selection.
- **Batch Download Support**: Allows batch downloading via text file containing multiple URLs.
- **Update Checker**: Automatically checks for new versions and prompts the user to download if available.
- **Logging**: Logs each download entry in `download_history.csv`, including URL, timestamp, and status.
- **User Interface**: Interactive CLI with clear prompts and guidance for each feature.
- **Help Menu**: Built-in help option explaining usage and platform-specific instructions.

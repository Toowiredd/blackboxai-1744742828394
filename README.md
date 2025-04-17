# Interactive 3D Dashboard Roadmap

## Overview

This project is an interactive 3D dashboard that allows users to configure and interact with 3D buttons and panels in real-time. The dashboard is built using Flask for the backend and Three.js for the frontend.

## Features

- **Headless Browser Capture**: Capture headless browser content using Puppeteer or Playwright.
- **Authentication and Security**: Secure the application using Flask-Login for authentication and add security measures.
- **Button Configuration Persistence**: Persist button configurations in a file or database and retrieve them on client connect.
- **Real-Time Synchronization**: Synchronize button states across clients using Socket.IO.
- **Live Content Embedding**: Embed live or streamed web content inside 3D panels with texture updates.
- **UI/UX Improvements**: Enhance the user interface with presets, tooltips, and onboarding tutorials.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Toowiredd/Interactive-3D-Dashboard-Roadmap.git
   cd Interactive-3D-Dashboard-Roadmap
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r flask3d/requirements.txt
   ```

4. Install Node.js and npm (if not already installed):
   ```bash
   # For macOS
   brew install node

   # For Ubuntu
   sudo apt-get install nodejs npm
   ```

5. Install Puppeteer or Playwright:
   ```bash
   npm install puppeteer
   # or
   npm install playwright
   ```

## Usage

1. Start the Flask application:
   ```bash
   python flask3d/app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`.

## API Endpoints

- **POST /api/button/config**: Update button configuration.
- **GET /api/button/config**: Retrieve all saved button configurations.
- **POST /api/browser/capture**: Capture headless browser content.

## Testing

1. Run the unit and integration tests:
   ```bash
   pytest
   ```

## Roadmap

Refer to the `flask3d/ROADMAP.md` file for a detailed roadmap of the project.

## License

This project is licensed under the MIT License.

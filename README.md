# File Converter Backend 🐍⚡

## 🌟 Project Overview
This is the backend API for my personal File Converter project. It handles file uploads, processes conversions between formats like PDF, MP3, MP4, images, and returns the converted files.
Built with FastAPI for fast, async, and easy-to-maintain backend service.

## 🛠 Tech Stack
- Python 3.10+
- FastAPI – Modern, fast web framework for building APIs
- Uvicorn – ASGI server for running FastAPI apps
- Pydantic – Data validation and settings management
- Various libraries for file processing and conversion (e.g., moviepy, Pillow, etc.)

## 🌈 Key Features
- Accepts multiple file formats for upload
- Processes conversions asynchronously
- Returns converted files for download
- Clear API endpoints with automatic Swagger docs
- Error handling for unsupported file types or failed conversions

## 🚀 Quick Start

### Prerequisites
Python 3.10+
pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/Wheezy049/FileConverter-BE.git
cd file-converter-backend
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the server
```bash
uvicorn app.main:app --reload
```

5. Access API docs
```bash
Open http://localhost:8000/docs in your browser to explore the API endpoints.
```

## 🔄 API Overview

| Endpoint                     | Method | Description               |
|------------------------------|--------|---------------------------|
| `/api/v1/convert/png-to-pdf` | POST   | Request file conversion   |
| `/api/v1/compress`            | POST   | Request file compression  |
| `/api/v1/download/{fileId}`   | POST   | Download converted file   |

**Built with ❤️ by Olatoyese Faruq**
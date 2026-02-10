Automated system to convert KTU exam result PDFs into structured Excel reports.
Features

PDF to Excel Conversion - Parse KTU result PDFs and generate organized spreadsheets
Department-wise Separation - Automatic grouping by engineering branches (CSE, ECE, EEE, ME, CE)
Pass/Fail Analysis - Built-in status tracking and summary statistics
User Authentication - Secure JWT-based login system
Session Persistence - SQLite database stores upload history

Tech Stack
Backend:

Python 3.x
FastAPI
PyPDF2 (PDF parsing)
pandas + openpyxl (Excel generation)
SQLite (session storage)

Frontend:

React 18
Vite
GSAP (animations)

Installation
Backend Setup
bash# Install dependencies
pip install -r requirements.txt

# Start server
cd backend
python main.py
Server runs at http://localhost:8000
Frontend Setup
bash# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

## Usage

1. **Register/Login** - Create an account or sign in
2. **Upload PDF** - Select your KTU result PDF file
3. **Process** - Click "Process File" to parse the document
4. **Download** - Get the generated Excel report

## Project Structure
```
├── backend/
│   ├── main.py           # FastAPI server
│   ├── pdf_parser.py     # PDF text extraction + regex parsing
│   ├── excel_generator.py # Excel file generation
│   └── auth.py           # JWT authentication
├── database/
│   └── database.py       # SQLite operations
├── frontend/
│   └── src/
│       ├── App.jsx       # Main application
│       └── Auth.jsx      # Login/Register component
└── requirements.txt
Excel Output Format
Generated Excel files include:

Department Sheets - Separate tabs for CSE, ECE, EEE, ME, CE
Summary Statistics - Total students, pass/fail counts, percentages
Color Coding - Failed grades highlighted in red
Formatted Headers - Professional styling with bold headers

API Endpoints
EndpointMethodDescription/healthGETServer status check/registerPOSTCreate new user account/loginPOSTAuthenticate user/uploadPOSTUpload and process PDF/download/{session_id}GETDownload generated Excel/sessionsGETView upload history
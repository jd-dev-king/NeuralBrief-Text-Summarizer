# NeuralBrief Text Summarizer

NeuralBrief is a full-stack extractive text summarization application built with Python, Flask, Gensim, HTML, CSS, and JavaScript.

The application allows users to paste long-form text or upload TXT, DOCX, and PDF documents, then condenses the content into a shorter summary using TF-IDF sentence modeling and PageRank-based ranking.

No login, account, or database is required.

## Live Demo

GitHub Pages frontend:

`https://jd-dev-king.github.io/NeuralBrief-Text-Summarizer/`

The GitHub Pages version hosts the static user interface. The Python Flask backend must be deployed separately for live summarization to function online.

## Features

* Paste articles, reports, or long-form text
* Upload TXT, DOCX, and PDF documents
* Generate extractive summaries
* Adjustable summary retention from 10% to 50%
* Default summary length of 20%
* Copy generated summaries to the clipboard
* Download summaries as TXT files
* Display original and summary word counts
* Display sentence-retention statistics
* Display output-length percentage
* Display processing time
* Drag-and-drop document upload
* Responsive high-tech user interface
* No authentication required
* No database required

## Technology Stack

### Backend

* Python
* Flask
* Flask-CORS
* Gensim
* NetworkX
* NumPy
* SciPy
* python-docx
* pypdf
* Werkzeug

### Frontend

* HTML5
* CSS3
* JavaScript
* Fetch API
* GitHub Pages

## How the Summarizer Works

NeuralBrief uses extractive summarization. Instead of generating new sentences, it selects the most important sentences directly from the original document.

The summarization pipeline:

1. Cleans and normalizes the source text.
2. Divides the text into sentences.
3. Tokenizes each sentence with Gensim.
4. Creates a Gensim dictionary and bag-of-words corpus.
5. Generates TF-IDF sentence representations.
6. Calculates cosine similarity between sentences.
7. Builds a sentence-similarity graph.
8. Uses PageRank to rank sentence importance.
9. Selects the highest-ranked sentences.
10. Restores the selected sentences to their original document order.

Because sentence lengths vary, a 20% sentence-retention setting may not produce exactly 20% of the original word count.

## Supported Documents

| Format                 | Support |
| ---------------------- | ------- |
| TXT                    | Yes     |
| DOCX                   | Yes     |
| PDF                    | Yes     |
| Scanned image-only PDF | No      |

Image-only PDFs require optical character recognition, which is not included in the current version.

## Project Structure

```text
NeuralBrief-Text-Summarizer/
├── backend/
│   ├── uploads/
│   │   └── .gitkeep
│   ├── app.py
│   ├── config.py
│   ├── document_reader.py
│   ├── requirements.txt
│   ├── summarizer.py
│   ├── test_document_reader.py
│   ├── test_environment.py
│   └── test_summarizer.py
│
├── frontend/
│   ├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
│
├── docs/
│   ├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   ├── .nojekyll
│   └── index.html
│
├── .gitignore
└── README.md
```

## Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/jd-dev-king/NeuralBrief-Text-Summarizer.git
cd NeuralBrief-Text-Summarizer
```

### 2. Enter the backend folder

```bash
cd backend
```

### 3. Create a virtual environment

On macOS or Linux:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
py -3.10 -m venv .venv
.venv\Scripts\activate
```

### 4. Install the dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### 5. Start the Flask application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Health Check

```http
GET /api/health
```

Example response:

```json
{
  "success": true,
  "service": "NeuralBrief Text Summarizer API",
  "status": "online",
  "default_summary_ratio": 0.2,
  "supported_files": [
    "docx",
    "pdf",
    "txt"
  ]
}
```

### Summarize Pasted Text

```http
POST /api/summarize
```

Example request:

```json
{
  "text": "Long article or document text...",
  "ratio": 0.2
}
```

Example response:

```json
{
  "success": true,
  "summary": "Generated extractive summary...",
  "statistics": {
    "original_words": 1250,
    "summary_words": 245,
    "original_sentences": 54,
    "summary_sentences": 11,
    "compression_percentage": 19.6,
    "processing_seconds": 0.18
  }
}
```

### Upload and Summarize a Document

```http
POST /api/upload
```

The request must use multipart form data with:

```text
file: uploaded document
ratio: summary ratio
```

Supported ratio values range from:

```text
0.10 to 0.50
```

## Testing

Run the environment test:

```bash
python test_environment.py
```

Run the summarizer test:

```bash
python test_summarizer.py
```

Run the document reader test:

```bash
python test_document_reader.py
```

## GitHub Pages

The static GitHub Pages version is stored in:

```text
docs/
```

GitHub Pages should be configured to deploy from:

```text
Branch: main
Folder: /docs
```

The frontend hosted on GitHub Pages cannot directly run the Python Flask backend. A public backend deployment URL must be added to:

```text
docs/js/app.js
```

Update:

```javascript
const DEPLOYED_API_URL = "";
```

with the deployed backend URL:

```javascript
const DEPLOYED_API_URL =
    "https://your-public-backend-url.com";
```

## Privacy and File Handling

* No account is required.
* No user information is stored in a database.
* Uploaded files are temporarily saved for processing.
* Temporary uploaded files are deleted after processing.
* The default maximum upload size is 10 MB.

## Current Limitations

* The application does not support scanned image-only PDFs.
* Extractive summaries may contain transitions that depend on omitted sentences.
* Summary length is based primarily on sentence retention rather than exact word count.
* The GitHub Pages version requires a separately deployed Flask API.
* The current version is optimized primarily for English-language text.

## Future Improvements

* Deploy the Flask API to a public hosting service
* Add keyword and key-phrase extraction
* Add URL-based article import
* Add article scraping support
* Add OCR support for scanned PDFs
* Add multiple summary modes
* Add sentence highlighting
* Add export to DOCX and PDF
* Add language detection
* Add automated testing
* Add Docker support
* Add backend rate limiting

## Portfolio Skills Demonstrated

This project demonstrates experience with:

* Natural language processing
* Extractive text summarization
* Gensim TF-IDF modeling
* PageRank sentence ranking
* Python application development
* Flask REST API development
* Document parsing
* File upload validation
* Responsive web interface design
* JavaScript Fetch API integration
* Git and GitHub
* GitHub Pages deployment

## Author

**Jeremiah Lupton**

GitHub: `https://github.com/jd-dev-king`

## License

This project is intended for educational and portfolio use.

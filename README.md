# SiliconSeal

**Automated Optical Inspection System for IC Marking Verification & Counterfeit Detection**

Built for **Bharat Electronics Limited (BEL)** as part of **Smart India Hackathon 2025 — Finals**
**Problem Statement ID: 25162**

---

## Live Demo

| Service | URL |
|---------|-----|
| **Frontend** | [https://siliconseal.onrender.com](https://siliconseal.onrender.com) |
| **Backend API** | [https://saif-ali-11-siliconseal-api.hf.space](https://saif-ali-11-siliconseal-api.hf.space) |
| **API Docs** | [https://saif-ali-11-siliconseal-api.hf.space/docs](https://saif-ali-11-siliconseal-api.hf.space/docs) (Swagger UI) |

> **Note:** The backend runs on Hugging Face Spaces free tier and sleeps after 15 minutes of inactivity. First request after that takes ~60 seconds to wake up. The frontend will show a banner with a link to wake the backend — just click it, wait, and retry.

**Demo credentials:** Username: `admin` | Password: `sih25162admin`

---

## What is SiliconSeal?

SiliconSeal is an AI-powered system that verifies whether an Integrated Circuit (IC) chip is **genuine or counterfeit** by analyzing the text markings printed on it.

Counterfeit ICs are a serious problem in defense and aerospace — fake chips can cause system failures in critical equipment. SiliconSeal automates the inspection process that is traditionally done manually under a microscope.

### How it works

```
Image Upload → YOLO Detection → PaddleOCR → Pattern Matching → Scoring → AI Analysis → Verdict
```

1. **Upload** an image of an IC chip (or use the camera)
2. **YOLOv8** detects and crops the IC region from the image
3. **PaddleOCR** extracts text (part number, date code, lot code, logo)
4. **Verification engine** matches extracted text against known patterns using Regex or Aho-Corasick algorithms
5. **Scoring engine** calculates weighted confidence (Part: 60%, Date: 25%, Lot: 15%)
6. **AI Agent** (Llama 3.3 70B via Groq) provides natural language risk assessment
7. Returns verdict: **GENUINE** / **FAKE** / **UNCERTAIN**

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (Python 3.11) |
| Object Detection | YOLOv8 (Ultralytics) |
| OCR Engine | PaddleOCR |
| Verification | Regex + Aho-Corasick Trie |
| AI Agent | Groq API (Llama 3.3 70B) |
| Auth | JWT (python-jose + bcrypt) |
| Image Processing | OpenCV, Pillow, NumPy |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 19 |
| Build Tool | Vite |
| Styling | Tailwind CSS v4 |
| Animations | Framer Motion |
| HTTP Client | Axios |
| File Upload | React Dropzone |
| Icons | Lucide React |

### Deployment
| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Render (Static Site) | [siliconseal.onrender.com](https://siliconseal.onrender.com) |
| Backend | Hugging Face Spaces (Docker) | [saif-ali-11-siliconseal-api.hf.space](https://saif-ali-11-siliconseal-api.hf.space) |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│         React + Vite + Tailwind CSS + Framer Motion      │
│   Home │ Scan │ Batch │ Live Camera │ Admin │ Architecture│
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS (REST API)
┌──────────────────────▼──────────────────────────────────┐
│                      API LAYER                           │
│              FastAPI + JWT Auth + CORS                   │
│   /scan │ /scan/batch │ /scan/frame │ /kb │ /ai/analyze  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  DETECTION LAYER                         │
│                YOLOv8 (Ultralytics)                      │
│        IC region detection and cropping                  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    OCR LAYER                              │
│                   PaddleOCR                               │
│   Multi-pass extraction │ Confidence filtering │ Grouping │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               VERIFICATION LAYER                         │
│     Regex (known IC) │ Aho-Corasick (auto-detect)        │
│   Pattern matching against Knowledge Base (27+ ICs)      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 SCORING ENGINE                            │
│  Weighted: Part 60% │ Date 25% │ Lot 15% │ Logo bonus   │
│  GENUINE (≥85%) │ UNCERTAIN (50-84%) │ FAKE (<50%)       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  AI AGENT LAYER                           │
│           Groq API │ Llama 3.3 70B Versatile             │
│  Verdict explanation │ Risk assessment │ Recommendations  │
└─────────────────────────────────────────────────────────┘
```

---

## Features

- **3 Scanning Modes** — Single upload, batch (up to 20 images), live camera
- **Dual Verification Algorithms** — Regex for known ICs, Aho-Corasick trie for auto-detection
- **AI-Powered Analysis** — Groq LLM explains verdicts in plain English with risk factors
- **Dark / Light Mode** — System preference detection with manual toggle
- **JWT Authentication** — Admin endpoints protected with Bearer tokens
- **Demo IC Images** — Canvas-generated test images for trying without real hardware
- **Animated Pipeline** — Step-by-step flow animation on each scan page
- **Backend Health Monitor** — Auto-detects when backend is offline with retry button
- **Knowledge Base** — 27+ IC entries with OCR-tolerant regex patterns
- **Mouser API Integration** — Auto-enrich KB with real IC data
- **YYWW Date Validation** — Future dates = instant FAKE verdict

---

## API Endpoints

### Public
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/api/v1/health` | Service health status |
| GET | `/api/v1/parts` | List all IC part IDs |
| POST | `/api/v1/scan` | Single image verification |
| POST | `/api/v1/scan/frame` | Base64 frame (live camera) |
| POST | `/api/v1/scan/batch` | Batch image verification |
| GET | `/api/v1/ai/status` | AI agent configuration status |
| POST | `/api/v1/ai/analyze` | Standalone AI analysis |

### Admin (JWT required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Get JWT token |
| GET | `/api/v1/kb` | View all KB entries |
| GET | `/api/v1/kb/{part_id}` | View specific KB entry |
| POST | `/api/v1/admin/reload-kb` | Rebuild KB index |
| POST | `/api/v1/admin/kb/enrich-and-save` | Fetch IC from Mouser & save |
| POST | `/api/v1/ai/generate-patterns` | AI-generate regex patterns |

---

## Local Setup Guide

### Prerequisites

Make sure you have these installed:

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Git** — [Download](https://git-scm.com/downloads)
- **uv** (Python package manager) — Install with: `pip install uv`

### Step 1: Clone the repository

```bash
git clone https://github.com/CommitSaif11/SiliconSeal.git
cd SiliconSeal
```

### Step 2: Set up the backend

```bash
cd backend
```

**Create virtual environment and install dependencies:**

```bash
uv venv
uv pip install -r requirements.txt
```

> On Windows, if `uv` is not recognized, use `python -m pip install uv` first.

**Create the `.env` file:**

Copy the example and fill in your keys:

```bash
cp .env.example .env
```

Open `.env` and set these values:

```env
SECRET_KEY=any-random-string-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$biotuykbclBb091OflZ2UeJaylDwYLa/pEkMfBv7dN1f4trn7w7ve
GROQ_API_KEY=your-groq-api-key-from-console.groq.com
MOUSER_API_KEY=your-mouser-key-if-you-have-one
```

> To generate your own admin password hash:
> ```bash
> python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
> ```

**Start the backend server:**

```bash
cd src
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be running at `http://localhost:8000`. Open `http://localhost:8000/docs` to see the Swagger UI.

### Step 3: Set up the frontend

Open a **new terminal** and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be running at `http://localhost:5173`.

### Step 4: Test it

1. Open `http://localhost:5173` in your browser
2. The status indicator should show "Backend: Connected"
3. Go to **Scan** → click any demo IC image → click **Verify IC**
4. To test admin features: click **Admin Login** → username: `admin`, password: `sih25162admin`

---

## Project Structure

```
SiliconSeal/
├── backend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── main.py              # FastAPI entry point
│   │   │   └── routers/
│   │   │       ├── api.py            # Core scan endpoints
│   │   │       ├── auth.py           # JWT login endpoint
│   │   │       ├── ai.py             # AI analysis endpoints
│   │   │       └── kb_admin.py       # KB management endpoints
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic settings
│   │   │   ├── auth.py               # JWT + bcrypt auth
│   │   │   ├── schemas.py            # Request/response models
│   │   │   └── models.py             # Data models
│   │   ├── engine/
│   │   │   ├── kb_loader.py          # Knowledge base file loader
│   │   │   └── kb_index.py           # Regex + Aho-Corasick index
│   │   ├── kb/
│   │   │   └── kb.json               # IC pattern database (27+ entries)
│   │   ├── pipeline/
│   │   │   ├── pipeline.py           # Orchestrator: YOLO → OCR → Verify
│   │   │   ├── detector/             # YOLOv8 IC detection
│   │   │   ├── ocr/                  # PaddleOCR text extraction
│   │   │   ├── verify/               # Regex + Aho-Corasick verification
│   │   │   └── intelligence/         # AI agent + Mouser API
│   │   └── utils/
│   │       └── image_utils.py        # Image encode/decode/resize
│   ├── Dockerfile                    # HF Spaces deployment
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment template
│   └── pyproject.toml                # Project metadata
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Nav with SIH/BEL badges
│   │   │   ├── BackendBanner.jsx     # Offline detection banner
│   │   │   ├── VerdictCard.jsx       # Scan result display
│   │   │   ├── PipelineBanner.jsx    # Animated pipeline steps
│   │   │   └── PageTransition.jsx    # Page entrance animations
│   │   ├── pages/
│   │   │   ├── Home.jsx              # Landing page with features
│   │   │   ├── Scan.jsx              # Single IC scan
│   │   │   ├── BatchScan.jsx         # Multi-image batch scan
│   │   │   ├── LiveScan.jsx          # Camera-based scanning
│   │   │   ├── Login.jsx             # Admin login
│   │   │   ├── Admin.jsx             # Admin dashboard
│   │   │   ├── Architecture.jsx      # System architecture detail
│   │   │   └── NotFound.jsx          # 404 page
│   │   ├── context/                  # Theme + Auth providers
│   │   ├── hooks/                    # Backend status hook
│   │   └── utils/
│   │       ├── api.js                # Axios API client
│   │       └── demoImages.js         # Canvas-generated IC images
│   └── package.json
└── render.yaml                       # Render deployment config
```

---

## Security

- JWT Bearer token authentication on all admin endpoints
- bcrypt password hashing (no plaintext storage)
- CORS whitelist (configurable, not wildcard)
- File upload size limits (10MB per file, 20 files per batch)
- Base64 input validation and size checking
- Environment-based secrets (`.env` is gitignored)

---

## Credits

**Smart India Hackathon 2025 — Grand Finale**
Problem Statement ID: **25162**
Organization: **Bharat Electronics Limited (BEL)**

Built by **Saif** ([@CommitSaif11](https://github.com/CommitSaif11))

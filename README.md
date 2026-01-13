# 🔍 JobLens - Job Market Intelligence Platform

<div align="center">

![JobLens Logo](https://img.shields.io/badge/JobLens-Intelligence%20Platform-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)

**An end-to-end job market intelligence system that aggregates real job postings, processes them through a backend analytics pipeline, and visualizes geographic job demand using interactive heatmaps and clustered maps.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org) [![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [🚀 What JobLens Does](#-what-joblens-does)
- [🧠 Why JobLens Is Different](#-why-joblens-is-different)
- [🏗️ System Architecture](#️-system-architecture)
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Project Structure](#-project-structure)
- [⚙️ Quick Start](#️-quick-start)
- [🔧 Configuration](#-configuration)
- [📊 Usage](#-usage)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 What JobLens Does

JobLens transforms raw job market data into actionable geographic insights:

- **🔄 Real-time Data Ingestion** - Connects to external job APIs (Adzuna) for live data
- **🗄️ Intelligent Storage** - Normalizes and stores job data in a geo-enabled PostgreSQL database
- **📍 Location Aggregation** - Groups job demand by geographic regions
- **🎨 Interactive Visualization** - Creates dynamic heatmaps and clustered markers
- **🎛️ Smart Filtering** - Provides backend-driven filters for roles and experience levels

> **All filtering and aggregation is performed server-side**, ensuring scalability and performance.

---

## 🧠 Why JobLens Is Different

<table>
<tr>
<th>❌ Most Job Market Projects</th>
<th>✅ JobLens Approach</th>
</tr>
<tr>
<td>
• Rely on static CSV datasets<br>
• Apply filters on the frontend<br>
• Don't scale beyond small datasets<br>
• Limited geographic analysis
</td>
<td>
• Uses real ingestion pipeline<br>
• Database-level filtering with SQL<br>
• PostgreSQL + PostGIS for geospatial queries<br>
• Clean separation of concerns
</td>
</tr>
</table>

**JobLens mirrors how real analytics platforms are built** - with proper data engineering, scalable backend architecture, and efficient visualization.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Adzuna Job API] --> B[Python Ingestion Pipeline]
    B --> C[PostgreSQL + PostGIS Database]
    C --> D[FastAPI Backend]
    D --> E[Streamlit Frontend]
    E --> F[Interactive Maps & Filters]
```

---

## ✨ Key Features

### 🔥 Job Demand Heatmap
- **Density-based visualization** of job market demand
- **City-level aggregation** for clear geographic insights
- **Performance optimized** for large datasets

### 📍 Clustered Markers
- **Zoom-aware clustering** that adapts to map level
- **Job concentration indicators** per geographic region
- **Smooth transitions** from macro to micro views

### 🎛️ Backend-Driven Filters
- **Role-based filtering** across job categories
- **Experience range selection** (entry-level to senior)
- **SQL-powered queries** for instant results

### 🧠 Experience Extraction
- **Regex-based NLP** parsing from job descriptions
- **Structured data conversion** from unstructured text
- **Meaningful analytics** on experience requirements

---
<!-- 
## 🛠️ Tech Stack

<div align="center">

### Backend & Data
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

### Frontend & Visualization
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PyDeck](https://img.shields.io/badge/PyDeck-WebGL-orange?style=for-the-badge)

### Development & Tools
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

</div> -->

---

## 📂 Project Structure

```
joblens/
├── 📁 backend/
│   ├── 🐍 main.py              # FastAPI application entry point
│   ├── 🗄️ database.py          # Database connection & configuration
│   ├── 📊 models.py            # SQLAlchemy ORM models
│   ├── 🔄 ingest_adzuna.py     # Job data ingestion pipeline
│   └── 🛠️ utils.py             # Utility functions
│
├── 📁 frontend/
│   └── 🎨 app.py               # Streamlit web application
│
├── 📁 data/
│   ├── 📋 roles.csv            # Job role categories
│   └── 🎯 skills.csv           # Skills taxonomy
│
├── ⚙️ .env.example             # Environment variables template
├── 📦 requirements.txt         # Python dependencies
├── 🐳 Dockerfile              # Container configuration
└── 📖 README.md               # Project documentation
```

---

## ⚙️ Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 13+ with PostGIS extension
- Git

### 1️⃣ Clone & Setup
```bash
# Clone the repository
git clone https://github.com/subham-sharma21/JobLens.git
cd JobLens

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Database Setup
```bash
# Install PostgreSQL and PostGIS
# Create database
createdb joblens
psql joblens -c "CREATE EXTENSION postgis;"
```

### 4️⃣ Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# DATABASE_URL=postgresql://username:password@localhost/joblens
# ADZUNA_API_KEY=your_api_key
# ADZUNA_APP_ID=your_app_id
```

### 5️⃣ Launch Application
```bash
# Terminal 1: Start backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Start frontend
streamlit run frontend/app.py --server.port 8501
```

<!-- ### 6️⃣ Access Application
- **Frontend**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health -->

---

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `ADZUNA_API_KEY` | Adzuna API key for job data | ✅ |
| `ADZUNA_APP_ID` | Adzuna application ID | ✅ |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | ❌ |
| `MAX_JOBS_PER_REQUEST` | Maximum jobs to fetch per API call | ❌ |

### API Configuration
```python
# backend/config.py
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"
DEFAULT_COUNTRY = "us"  # United States
DEFAULT_LOCATION = "new york"
```

---

## 📊 Usage

### Data Ingestion
```bash
# Run job data ingestion
python backend/ingest_adzuna.py --location "san francisco" --pages 10
```

### API Endpoints
- `GET /jobs` - Retrieve filtered job data
- `GET /jobs/heatmap` - Get heatmap data points
- `GET /jobs/clusters` - Get clustered marker data
- `GET /stats` - Get job market statistics

### Frontend Features
- **Interactive Map**: Pan, zoom, and explore job concentrations
- **Dynamic Filters**: Filter by role, experience, and location
- **Real-time Updates**: Data refreshes automatically
- **Export Options**: Download filtered datasets

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .
isort .

# Linting
flake8 .
```

### Reporting Issues
Please use our [Issue Template](.github/ISSUE_TEMPLATE.md) when reporting bugs or requesting features.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Subham Sharma](https://github.com/subham-sharma21)**

⭐ **Star this repo if you find it helpful!** ⭐

</div>
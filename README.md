# 🔍 JobLens — Job Market Intelligence Platform

**JobLens** is an end-to-end job market intelligence system that aggregates real job postings, processes them through a backend analytics pipeline, and visualizes **geographic job demand** using interactive heatmaps and clustered maps.

This project is built with a **production-first mindset**, focusing on data engineering, backend-driven analytics, and scalable geospatial visualization.



## 🚀 What JobLens Does

- Ingests real job data from external APIs
- Normalizes and stores job data in a geo-enabled database
- Aggregates job demand by location
- Visualizes demand using:
  - Heatmaps (density-based)
  - Clustered markers (zoom-aware)
- Supports backend-driven filters:
  - Role
  - Experience range

All filtering and aggregation is performed **server-side**, not in the UI.



## 🧠 Why JobLens Is Different

Most job market projects:
- Rely on static CSV datasets
- Apply filters on the frontend
- Do not scale beyond small datasets

**JobLens**:
- Uses a real ingestion pipeline
- Applies filters at the database level
- Uses **PostgreSQL + PostGIS** for geospatial queries
- Cleanly separates ingestion, API, and visualization layers

This mirrors how real analytics platforms are built.



- [🔍 JobLens — Job Market Intelligence Platform](#-joblens--job-market-intelligence-platform)
  - [🚀 What JobLens Does](#-what-joblens-does)
  - [🧠 Why JobLens Is Different](#-why-joblens-is-different)
  - [🏗️ System Architecture](#️-system-architecture)
  - [🧩 Key Features](#-key-features)
    - [🔥 Job Demand Heatmap](#-job-demand-heatmap)
    - [📍 Clustered Markers](#-clustered-markers)
    - [🎛️ Backend-Driven Filters](#️-backend-driven-filters)
    - [🧠 Experience Extraction](#-experience-extraction)
  - [🛠️ Tech Stack](#️-tech-stack)
    - [Backend](#backend)
    - [Data \& Processing](#data--processing)
    - [Frontend](#frontend)
    - [Dev \& Environment](#dev--environment)
  - [📂 Project Structure](#-project-structure)
  - [⚙️ Local Setup \& Run](#️-local-setup--run)
    - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
    - [2️⃣ Create Virtual Environment](#2️⃣-create-virtual-environment)
    - [3️⃣ Install Dependencies](#3️⃣-install-dependencies)
    - [4️⃣ Configure Environment Variables](#4️⃣-configure-environment-variables)
    - [5️⃣ Start Backend](#5️⃣-start-backend)
    - [6️⃣ Run Frontend](#6️⃣-run-frontend)
    - [📊 Example Use Cases](#-example-use-cases)
    - [🧪 Current Limitations](#-current-limitations)
    - [🔮 Planned Enhancements](#-planned-enhancements)
    - [🧠 What This Project Demonstrates](#-what-this-project-demonstrates)
    - [📜 License](#-license)
    - [🙌 Author Notes](#-author-notes)



## 🏗️ System Architecture
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [🔍 JobLens — Job Market Intelligence Platform](#-joblens--job-market-intelligence-platform)
  - [🚀 What JobLens Does](#-what-joblens-does)
  - [🧠 Why JobLens Is Different](#-why-joblens-is-different)
  - [🏗️ System Architecture](#️-system-architecture)
  - [🧩 Key Features](#-key-features)
    - [🔥 Job Demand Heatmap](#-job-demand-heatmap)
    - [📍 Clustered Markers](#-clustered-markers)
    - [🎛️ Backend-Driven Filters](#️-backend-driven-filters)
    - [🧠 Experience Extraction](#-experience-extraction)
  - [🛠️ Tech Stack](#️-tech-stack)
    - [Backend](#backend)
    - [Data & Processing](#data--processing)
    - [Frontend](#frontend)
    - [Dev & Environment](#dev--environment)
  - [📂 Project Structure](#-project-structure)
  - [⚙️ Local Setup & Run](#️-local-setup--run)
    - [1️⃣ Clone the Repository](#1️⃣-clone-the-repository)
    - [2️⃣ Create Virtual Environment](#2️⃣-create-virtual-environment)
    - [3️⃣ Install Dependencies](#3️⃣-install-dependencies)
    - [4️⃣ Configure Environment Variables](#4️⃣-configure-environment-variables)
    - [5️⃣ Start Backend](#5️⃣-start-backend)
    - [6️⃣ Run Frontend](#6️⃣-run-frontend)
    - [📊 Example Use Cases](#-example-use-cases)
    - [🧪 Current Limitations](#-current-limitations)
    - [🔮 Planned Enhancements](#-planned-enhancements)
    - [🧠 What This Project Demonstrates](#-what-this-project-demonstrates)
    - [📜 License](#-license)
    - [🙌 Author Notes](#-author-notes)

<!-- /code_chunk_output -->

```
Adzuna Job API
    ↓
Ingestion Pipeline (Python)
    ↓
PostgreSQL + PostGIS
    ↓
FastAPI Backend
    ↓
Streamlit Frontend (Maps + Filters)
```




## 🧩 Key Features

### 🔥 Job Demand Heatmap
- Density-based visualization of job demand
- Aggregated at city level
- Efficient even with growing data volume

### 📍 Clustered Markers
- Zoom-based clustered view
- Shows job concentration per city
- Smooth transition from macro to micro view

### 🎛️ Backend-Driven Filters
- Role-based filtering
- Experience range filtering
- Filters executed via SQL queries, not frontend logic

### 🧠 Experience Extraction
- Regex-based parsing from job descriptions
- Converts unstructured text into structured experience ranges
- Enables meaningful experience-based analysis


## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- PostGIS

### Data & Processing
- Requests
- Pandas
- Regex-based NLP (experience extraction)

### Frontend
- Streamlit
- PyDeck (WebGL-powered maps)

### Dev & Environment
- Virtual environments
- Environment variables (`.env`)
- Git-safe secret management


## 📂 Project Structure
```
joblens/
│
├── backend/
│ ├── main.py # FastAPI application
│ ├── database.py # Database connection
│ ├── models.py # ORM models
│ ├── ingest_adzuna.py # Job ingestion pipeline
│
├── frontend/
│ └── app.py # Streamlit UI
│
├── data/
│ ├── roles.csv
│ └── skills.csv
│
├── .env.example # Environment variable template
├── requirements.txt
└── README.md
```



## ⚙️ Local Setup & Run

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/joblens.git
cd joblens
```

### 2️⃣ Create Virtual Environment
```
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate    # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
```
Create a .env file using .env.example as reference.
```
### 5️⃣ Start Backend
```
uvicorn backend.main:app --reload
```

### 6️⃣ Run Frontend
```
streamlit run frontend/app.py
```

### 📊 Example Use Cases

Identify cities with the highest demand for data roles

Compare junior vs senior job distribution

Analyze geographic hiring concentration

Understand regional demand patterns

### 🧪 Current Limitations

Job data limited by API coverage

Skill extraction not yet enabled

Clustering is frontend-based (server-side clustering planned)

These are intentional trade-offs for stability and clarity.

### 🔮 Planned Enhancements

Skill extraction and skill-wise heatmaps

Salary normalization and analysis

Time-series job trend analysis

Server-side geo clustering

Cloud deployment (Render + Streamlit Cloud)

### 🧠 What This Project Demonstrates

Real-world data ingestion pipelines

Backend API design

Geospatial data handling

Scalable visualization patterns

Environment and secret management

Debugging and iterative system building

### 📜 License

MIT License

### 🙌 Author Notes

JobLens was built to reflect how real data products are designed, not tutorial shortcuts.

If you are reviewing this as a recruiter or engineer:

This project emphasizes architecture, data flow, and tradeoffs - not just visuals.
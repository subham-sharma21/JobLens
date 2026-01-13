#!/bin/bash

# Project root
PROJECT_NAME="job-market-map"

echo "Creating project structure: $PROJECT_NAME"

# Create root directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME || exit 1

# Backend structure
mkdir -p backend
touch backend/main.py
touch backend/database.py
touch backend/models.py
touch backend/ingest_adzuna.py
touch backend/utils.py

# Data structure
mkdir -p data
touch data/roles.csv
touch data/skills.csv

# Frontend structure
mkdir -p frontend
touch frontend/app.py

# Root files
touch requirements.txt
touch README.md

echo "✅ Project structure created successfully."

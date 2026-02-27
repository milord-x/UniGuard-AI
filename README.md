# UniGuard AI

UniGuard AI is an Academic Early Warning and Advisor Decision Support System designed to detect student academic risk at an early stage using explainable predictive analytics.

## Overview

Universities typically detect academic failure too late — after performance collapse occurs.

UniGuard AI provides:

- Early academic risk detection
- Student performance forecasting
- Explainable risk reasoning
- Automated advisor intervention plans
- Group-level analytics dashboard

The system operates as a **local web application** running entirely in the browser with a Python backend.

---

## System Architecture

Local Web App Model:

Browser UI  
↓  
FastAPI Backend  
↓  
Risk Engine  
↓  
SQLite Database

Modules:

- Risk Scoring Engine
- Academic Forecasting
- Advisor Dashboard
- Action Plan Generator
- AI Recommendation Chat

---

## Features

- 500 simulated students
- 15-week academic timeline
- Multi-subject evaluation
- Risk clustering (LOW / MEDIUM / HIGH)
- Explainable intervention planning
- Advisor analytics interface

---

## Technology Stack

Backend:
- Python 3.12+
- FastAPI
- SQLite
- OpenPyXL

Frontend:
- Vanilla JavaScript
- Local SPA architecture
- Canvas analytics visualization

---

## Running Locally

```bash
git clone https://github.com/milord-x/UniGuard_AI.git
cd UniGuard_AI

python -m venv .venv
source .venv/bin/activate.fish

pip install -r requirements.txt

set -x PYTHONPATH apps/backend
uvicorn uniguard.main:app --reload

Open: http://127.0.0.1:8000
---

# UniGuard AI

UniGuard AI is an academic early warning and advisor decision support system designed to detect student academic risk at an early stage using explainable predictive analytics.

## Overview

Universities typically detect academic failure too late, after performance collapse has already started.

UniGuard AI provides:

- early academic risk detection
- student performance forecasting
- explainable risk reasoning
- automated advisor intervention plans
- group-level analytics dashboards

The system is designed as a local web application with a browser frontend and a Python backend.

---

## System Architecture

Local web app model:

```text
Browser UI
  ↓
FastAPI backend
  ↓
Risk engine
  ↓
SQLite database
```

Core modules:

- Risk scoring engine
- Academic forecasting
- Advisor dashboard
- Action plan generator
- AI recommendation chat

---

## Features

- 500 simulated students
- 15-week academic timeline
- Multi-subject evaluation
- Risk clustering (`LOW` / `MEDIUM` / `HIGH`)
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
git clone https://github.com/milord-x/UniGuard-AI.git
cd UniGuard-AI

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export PYTHONPATH=apps/backend
uvicorn uniguard.main:app --reload
```

If you use `fish`, activate the environment with:

```bash
source .venv/bin/activate.fish
```

Then open:

```text
http://127.0.0.1:8000
```

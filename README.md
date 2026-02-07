# Academic Intelligence Engine

*A prototype of an academic intelligence system designed with intentionality, restraint, and architectural permanence.*

---

## Philosophy

This is not a feature-rich dashboard.  
This is not a typical student management system.

This is **intelligence infrastructure** disguised as a small application.

Advanced systems are not loud.  
They are **inevitable**.

---

## What This Is

An academic monitoring engine that:

- Thinks through deterministic reasoning, not external APIs  
- Observes student attendance and performance patterns  
- Predicts risk states before they become critical  
- Speaks only when necessary, with calm precision  
- Survives UI destruction — the intelligence layer remains functional  

The system is designed as a **device-agnostic interface**, delivering consistent intelligence and performance across platforms without platform-specific code.

This system is designed to **scale to institutions**, not overflow in hackathon demos.

---

## Architecture

The system follows **three-layer separation**:

### 1. Core Intelligence Layer (`src/core/`)
Pure Python modules with zero framework dependency:

- `student_manager.py` — Entity management with validation  
- `attendance_manager.py` — Attendance intelligence with risk detection  
- `performance_manager.py` — Performance classification and trend analysis  
- `ai_logic.py` — Rule-based reasoning engine generating calm insights  

**The system functions fully even if the UI is removed.**

---

### 2. Orchestration Layer (`src/app.py`)
Minimal Flask application serving as a bridge:

- REST API exposing intelligence  
- No business logic — pure orchestration  
- Flask is intentionally minimal  

---

### 3. Experience Layer (`templates/`, `static/`)
Calm, intelligence-first interface:

- Semantic HTML  
- Modern CSS with design tokens  
- Vanilla JavaScript (state-driven, no libraries)  
- Typography-first, dark aesthetic  
- Intentional animations for state changes only  

---

## Intelligence Features

### Attendance Intelligence
- Tracks total vs attended lectures  
- Calculates real-time attendance percentage  
- Detects risk states:
  - Critical (<75%)
  - Warning (75–80%, declining)
  - Stable
  - Excellent (>90%)
- Trend analysis to predict future risk  
- Calculates lectures required for recovery  

---

### Performance Intelligence
- Classifies performance:
  - Good (≥75)
  - Average (50–74)
  - Needs Improvement (<50)
- Assesses confidence:
  - Stable
  - Unstable
  - Improving
  - Declining
- Maintains performance history  
- Detects variance and inconsistency  

---

### AI Reasoning Engine
- **Not a model. Not an API. Pure deterministic logic.**
- Generates calm, explainable insights such as:
  - "Attendance is below threshold. Recovery requires 8 consecutive sessions."
  - "Performance stability requires attention."
- Composite risk scoring (0–100)
- Fully explainable — every output maps to rules  

---

### System Pulse
- Overall cohort attendance health  
- At-risk student count  
- Performance stability indicators  
- Maximum **two** system insights at a time  

---

## Technology Stack

| Layer | Technology | Rationale |
|-----|-----------|-----------|
| Core | Python 3.x | Readable, maintainable |
| Web | Flask | Minimal and unobtrusive |
| Frontend | HTML, CSS, Vanilla JS | Zero dependencies |
| Typography | Inter (Google Fonts) | Clean and professional |
| Database | None (In-memory) | Prototype phase |

**Every dependency is a liability. This system has almost none.**

---

## Installation & Usage

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
cd GVP_AI_Hackathon_2026
pip install flask
python src/app.py
```

Application runs at:
👉 `http://localhost:5000`

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Dashboard |
| GET | `/api/students` | Fetch students |
| POST | `/api/students` | Add student |
| PUT | `/api/students/<roll_number>` | Update student |
| DELETE | `/api/students/<roll_number>` | Remove student |
| GET | `/api/system/pulse` | System intelligence |

---

## Project Structure

```
GVP_AI_Hackathon_2026/
├── src/
│   ├── core/
│   └── app.py
├── templates/
├── static/
├── README.md
└── architecture.txt
```

---

## License

Prototype system for **GVP AI Hackathon 2026**.  
Built to demonstrate foundational system thinking.

---

## Contact

* Instagram: **@ojgauswami**
* GitHub: [https://github.com/ojgauswami](https://github.com/ojgauswami)

---

### Final Truth

You are not looking at a hackathon project.

You are looking at **the foundation of an inevitable system**.

That difference will be felt.

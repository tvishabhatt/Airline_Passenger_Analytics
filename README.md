# Airline Passenger Experience & Satisfaction Analytics Dashboard

> **Submitted by:** Tvisha Bhatt 
> **Dataset:** [airline_passenger_satisfaction.csv](./airline_passenger_satisfaction.csv) — 129,880 rows × 24 columns  
> **Tools:** Python · Pandas · NumPy · Plotly · Streamlit · Matplotlib · Seaborn

---

## Project Description

This project analyses real airline passenger satisfaction data to uncover what drives passenger satisfaction and dissatisfaction. The analysis covers:

- Service quality across **14 service areas** (Wi-Fi, Boarding, Seat Comfort, etc.)
- Satisfaction differences by **travel class**, **customer type**, and **travel type**
- Impact of **flight delays** on passenger satisfaction
- **Passenger demographics** — age, gender, and travel patterns
- **Actionable business recommendations** based on actual data findings

The final product is an **interactive Streamlit dashboard** backed by a reusable Python analysis module (`analysis.py`), supported by a Jupyter notebook and a full project report.

---

## Submitted Files

| File | Format | Description |
|---|---|---|
| `Tvisha_Airline_Passenger_Analytics.ipynb` | `.ipynb` | Complete analytical workflow (code file) |
| `requirements.txt` | `.txt` | Python dependencies |
| `Tvisha_ProjectReport.docx` | `.docx` | Full project documentation |
| `README.md` | `.md` | This file |

**Additional project files (supporting):**

| File | Description |
|---|---|
| `airline_passenger_satisfaction.csv` | Raw dataset — never modified |
| `analysis.py` | Central analysis module (single source of truth) |
| `app.py` | Streamlit interactive dashboard |

---

## Dataset

| Item | Value |
|---|---|
| File | `airline_passenger_satisfaction.csv` |
| Total records | **129,880** |
| Total columns | **24** |
| Target variable | `Satisfaction` — `Satisfied` / `Neutral or Dissatisfied` |
| Missing values | 393 rows in `Arrival Delay` only (0.30%) |
| Duplicate rows | 0 |

**Key columns:** ID, Gender, Age, Customer Type, Type of Travel, Class, Flight Distance, Departure Delay, Arrival Delay, 14 service-rating columns (0–5), Satisfaction.

---

## Technologies Used

| Package | Purpose |
|---|---|
| `pandas` | Data loading, cleaning, manipulation |
| `numpy` | Numerical calculations |
| `plotly` | Interactive charts in dashboard |
| `streamlit` | Interactive web dashboard |
| `matplotlib` | Static charts in notebook |
| `seaborn` | Statistical charts in notebook |
| `jupyter` | Running the `.ipynb` notebook |
| `openpyxl` | Excel supporting package |

---

## Setup & Installation

### Requirements
- Python 3.9 or higher
- pip

### Install all dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

### Run the Streamlit Dashboard

```bash
streamlit run app.py
```

Opens at **http://localhost:8501** — all filters, KPIs, and charts are interactive.

### Open the Jupyter Notebook

```bash
jupyter notebook Tvisha_Airline_Passenger_Analytics.ipynb
```

Run all cells from top to bottom. The notebook is fully self-contained — no external imports required.

---

## Key Findings

1. **43.45%** of passengers are satisfied; **56.55%** are Neutral or Dissatisfied.
2. **Business class** satisfaction (69.44%) is 3.7× higher than **Economy** (18.77%).
3. **Online Boarding** is the #1 differentiating service factor — a 1.37-point rating gap between satisfied and dissatisfied passengers.
4. **In-flight Wifi Service** is the lowest-rated area at 2.73/5.
5. **Personal travel passengers** are overwhelmingly dissatisfied — only 10.13% satisfied.
6. Delays reduce satisfaction by **~6.87 percentage points**.

---

## Business Recommendations

1. Upgrade **In-flight Wifi Service** — lowest-rated service area.
2. Improve **Online Boarding UX** — highest satisfaction impact factor.
3. Focus on **Economy class** service improvements — only 18.77% satisfied.
4. Build a dedicated programme for **Personal travel passengers** — 89.87% dissatisfied.
5. Reduce delays and improve **proactive delay communication**.
6. Create a **First-flyer onboarding programme** — only 23.97% satisfaction on first flight.

---

## Project Structure

```
Airline_Passenger_Analytics/
│
├── Tvisha_Airline_Passenger_Analytics.ipynb  ← Submit: code file (.ipynb)
├── requirements.txt                         ← Submit: requirements file (.txt)
├── Tvisha_ProjectReport.docx               ← Submit: project report (.docx)
├── README.md                               ← Submit: README file (.md)
│
├── airline_passenger_satisfaction.csv      ← Raw dataset (never modified)
├── analysis.py                             ← Central analysis module
└── app.py                                  ← Streamlit dashboard
```

---

## Limitations

- `Arrival Delay` has 393 missing values (0.30%) — imputed with column median.
- Service rating 0 may mean "not applicable" rather than a genuine worst rating.
- No flight route, airline name, or date information in the dataset.
- Satisfaction is a binary label — nuanced partial satisfaction cannot be measured.

---

_Airline Passenger Experience & Satisfaction Analytics Dashboard  - Bhatt Tvisha_

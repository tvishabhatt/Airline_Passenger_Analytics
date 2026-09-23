"""
analysis.py
===========
Central analytical module for the Airline Passenger Experience & Satisfaction Analytics project.

This module handles:
  - Loading the raw CSV
  - Data cleaning
  - Feature engineering
  - KPI calculations
  - Service-rating analysis
  - Satisfaction analysis
  - Business-question answers

All other project components (app.py, notebook) import from here so that
every number in the project comes from a single source of truth.
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CSV_PATH = "airline_passenger_satisfaction.csv"

# All 14 service-rating columns that appear in the dataset
SERVICE_COLS = [
    "Departure and Arrival Time Convenience",
    "Ease of Online Booking",
    "Check-in Service",
    "Online Boarding",
    "Gate Location",
    "On-board Service",
    "Seat Comfort",
    "Leg Room Service",
    "Cleanliness",
    "Food and Drink",
    "In-flight Service",
    "In-flight Wifi Service",
    "In-flight Entertainment",
    "Baggage Handling",
]

# Age-group bin edges and labels
AGE_BINS   = [0, 18, 30, 45, 60, 100]
AGE_LABELS = ["Under 18", "18–30", "31–45", "46–60", "60+"]

# Flight-distance category bin edges and labels
DIST_BINS   = [0, 500, 1500, 3000, 5000]
DIST_LABELS = ["Short (<500)", "Medium (500–1500)", "Long (1500–3000)", "Very Long (3000+)"]

# ---------------------------------------------------------------------------
# 1. Load Raw Data
# ---------------------------------------------------------------------------

def load_raw_data(path: str = CSV_PATH) -> pd.DataFrame:
    """Load the raw CSV without any modifications."""
    df = pd.read_csv(path)
    return df


# ---------------------------------------------------------------------------
# 2. Data Cleaning
# ---------------------------------------------------------------------------

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the raw dataframe and return the cleaned dataframe along with a
    dictionary that records every cleaning action taken.

    Cleaning steps:
      1. Record original shape.
      2. Remove exact duplicate rows (none expected, but checked).
      3. Convert 'Arrival Delay' to numeric and fill the 393 NaN values
         with the column median (the only column with missing values).
      4. Clip service-rating columns to [0, 5] (data already within range).
      5. Remove rows where Age is outside [7, 85] – none found in the data.
      6. Remove rows where Flight Distance <= 0 – none found in the data.
      7. Record final shape.
    """
    report = {}

    report["original_rows"]    = len(df)
    report["original_cols"]    = df.shape[1]
    report["duplicates_found"] = int(df.duplicated().sum())

    # Step 1 – drop exact duplicates
    df = df.drop_duplicates().reset_index(drop=True)

    # Step 2 – missing values
    missing_before = df.isnull().sum()
    report["missing_arrival_delay"] = int(missing_before["Arrival Delay"])

    arrival_median = df["Arrival Delay"].median()
    df["Arrival Delay"] = pd.to_numeric(df["Arrival Delay"], errors="coerce")
    df["Arrival Delay"] = df["Arrival Delay"].fillna(arrival_median)
    report["arrival_delay_fill_value"] = round(float(arrival_median), 2)

    # Step 3 – ensure numeric types for service cols, delay, distance
    for col in SERVICE_COLS + ["Flight Distance", "Departure Delay", "Age"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Step 4 – remove rows with invalid Age or Flight Distance (none expected)
    rows_before = len(df)
    df = df[df["Age"] >= 7]
    df = df[df["Flight Distance"] > 0]
    report["invalid_rows_removed"] = rows_before - len(df)

    report["final_rows"] = len(df)
    report["final_cols"] = df.shape[1]

    df = df.reset_index(drop=True)
    return df, report


# ---------------------------------------------------------------------------
# 3. Feature Engineering
# ---------------------------------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived analytical columns to the cleaned dataframe.

    New columns:
      - Total Delay        : Departure Delay + Arrival Delay (minutes)
      - Delay Status       : 'Delayed' if Total Delay > 0 else 'On Time'
      - Age Group          : Binned age ranges
      - Distance Category  : Binned flight-distance ranges
      - Avg Service Rating : Mean of all 14 service-rating columns
    """
    df = df.copy()

    # Total delay
    df["Total Delay"] = df["Departure Delay"] + df["Arrival Delay"]

    # Delay status
    df["Delay Status"] = df["Total Delay"].apply(
        lambda x: "Delayed" if x > 0 else "On Time"
    )

    # Age group
    df["Age Group"] = pd.cut(
        df["Age"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=True,
    ).astype(str)

    # Flight distance category
    df["Distance Category"] = pd.cut(
        df["Flight Distance"],
        bins=DIST_BINS,
        labels=DIST_LABELS,
        right=True,
    ).astype(str)

    # Average service rating across all 14 service columns
    df["Avg Service Rating"] = df[SERVICE_COLS].mean(axis=1).round(2)

    return df


# ---------------------------------------------------------------------------
# 4. Full Pipeline (load → clean → engineer)
# ---------------------------------------------------------------------------

def load_and_prepare(path: str = CSV_PATH) -> tuple[pd.DataFrame, dict]:
    """
    Convenience function: load the CSV, clean it, and add derived features.
    Returns (prepared_df, cleaning_report).
    """
    raw = load_raw_data(path)
    cleaned, report = clean_data(raw)
    prepared = engineer_features(cleaned)
    return prepared, report


# ---------------------------------------------------------------------------
# 5. KPI Calculations
# ---------------------------------------------------------------------------

def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate the main KPIs from the supplied (optionally filtered) dataframe.
    Returns a dictionary of KPI name → value.
    """
    if df.empty:
        return {
            "Total Passengers":       0,
            "Satisfied Passengers":   0,
            "Satisfaction Rate (%)":  0.0,
            "Average Age":            0.0,
            "Average Flight Distance":0.0,
            "Average Total Delay":    0.0,
            "Average Service Rating": 0.0,
        }

    total       = len(df)
    satisfied   = int((df["Satisfaction"] == "Satisfied").sum())
    sat_rate    = round(satisfied / total * 100, 2)
    avg_age     = round(df["Age"].mean(), 1)
    avg_dist    = round(df["Flight Distance"].mean(), 1)
    avg_delay   = round(df["Total Delay"].mean(), 1)
    avg_service = round(df["Avg Service Rating"].mean(), 2)

    return {
        "Total Passengers":        total,
        "Satisfied Passengers":    satisfied,
        "Satisfaction Rate (%)":   sat_rate,
        "Average Age":             avg_age,
        "Average Flight Distance": avg_dist,
        "Average Total Delay":     avg_delay,
        "Average Service Rating":  avg_service,
    }


# ---------------------------------------------------------------------------
# 6. Service-Rating Analysis
# ---------------------------------------------------------------------------

def service_rating_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a dataframe with mean service ratings for all 14 service columns,
    sorted descending by average rating.
    Columns: Service, Average Rating
    """
    means = df[SERVICE_COLS].mean().round(3)
    result = pd.DataFrame({
        "Service":        means.index,
        "Average Rating": means.values,
    }).sort_values("Average Rating", ascending=False).reset_index(drop=True)
    return result


def service_rating_by_satisfaction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a dataframe comparing mean service ratings between Satisfied and
    Neutral or Dissatisfied passengers.
    Columns: Service, Satisfied, Neutral or Dissatisfied, Difference
    """
    grp = df.groupby("Satisfaction")[SERVICE_COLS].mean().round(3).T
    grp.index.name = "Service"
    grp = grp.reset_index()

    # Ensure both columns exist (in case of filtered subset)
    for cat in ["Satisfied", "Neutral or Dissatisfied"]:
        if cat not in grp.columns:
            grp[cat] = np.nan

    grp["Difference"] = (grp["Satisfied"] - grp["Neutral or Dissatisfied"]).round(3)
    grp = grp.sort_values("Difference", ascending=False).reset_index(drop=True)
    return grp


# ---------------------------------------------------------------------------
# 7. Satisfaction Analysis Functions
# ---------------------------------------------------------------------------

def satisfaction_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Return satisfaction rates (%) for each unique value in `column`.
    Columns: <column>, Satisfied, Total, Satisfaction Rate (%)
    """
    grp = df.groupby(column)["Satisfaction"].apply(
        lambda s: pd.Series({
            "Satisfied":            (s == "Satisfied").sum(),
            "Total":                len(s),
            "Satisfaction Rate (%)": round((s == "Satisfied").mean() * 100, 2),
        })
    ).unstack().reset_index()
    grp["Satisfied"] = grp["Satisfied"].astype(int)
    grp["Total"]     = grp["Total"].astype(int)
    return grp


def satisfaction_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return overall satisfaction counts and percentages.
    Columns: Satisfaction, Count, Percentage
    """
    counts = df["Satisfaction"].value_counts().reset_index()
    counts.columns = ["Satisfaction", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


# ---------------------------------------------------------------------------
# 8. Delay Analysis
# ---------------------------------------------------------------------------

def delay_summary(df: pd.DataFrame) -> dict:
    """Summary statistics for delay columns."""
    if df.empty:
        return {}
    return {
        "avg_departure_delay": round(df["Departure Delay"].mean(), 2),
        "avg_arrival_delay":   round(df["Arrival Delay"].mean(), 2),
        "avg_total_delay":     round(df["Total Delay"].mean(), 2),
        "pct_on_time":         round((df["Delay Status"] == "On Time").mean() * 100, 2),
        "pct_delayed":         round((df["Delay Status"] == "Delayed").mean() * 100, 2),
    }


# ---------------------------------------------------------------------------
# 9. Business Question Answers
# ---------------------------------------------------------------------------

def answer_business_questions(df: pd.DataFrame) -> dict:
    """
    Calculate answers to all 13 business questions and return them in a dict.
    This function is used by the notebook and ensures consistent numbers.
    """
    answers = {}

    # Q1/Q2 — overall satisfaction split
    dist = satisfaction_distribution(df)
    for _, row in dist.iterrows():
        answers[f"pct_{row['Satisfaction'].replace(' ', '_').lower()}"] = row["Percentage"]

    # Q3 — satisfaction by Customer Type
    ct = satisfaction_by_column(df, "Customer Type")
    answers["customer_type_satisfaction"] = ct.set_index("Customer Type")["Satisfaction Rate (%)"].to_dict()

    # Q4 — satisfaction by Type of Travel
    tt = satisfaction_by_column(df, "Type of Travel")
    answers["travel_type_satisfaction"] = tt.set_index("Type of Travel")["Satisfaction Rate (%)"].to_dict()

    # Q5 — satisfaction by Class
    cl = satisfaction_by_column(df, "Class")
    answers["class_satisfaction"] = cl.set_index("Class")["Satisfaction Rate (%)"].to_dict()

    # Q6 — delays vs satisfaction
    ds = satisfaction_by_column(df, "Delay Status")
    answers["delay_status_satisfaction"] = ds.set_index("Delay Status")["Satisfaction Rate (%)"].to_dict()

    # Q7/Q8 — best and worst service areas
    svc = service_rating_summary(df)
    answers["best_service_area"]  = svc.iloc[0]["Service"]
    answers["best_service_rating"] = svc.iloc[0]["Average Rating"]
    answers["worst_service_area"] = svc.iloc[-1]["Service"]
    answers["worst_service_rating"] = svc.iloc[-1]["Average Rating"]

    # Q9 — largest rating difference between satisfied and dissatisfied
    svc_diff = service_rating_by_satisfaction(df)
    answers["largest_diff_service"]    = svc_diff.iloc[0]["Service"]
    answers["largest_diff_value"]      = svc_diff.iloc[0]["Difference"]

    # Q10 — online boarding by satisfaction
    ob = df.groupby("Satisfaction")["Online Boarding"].mean().round(3).to_dict()
    answers["online_boarding_by_satisfaction"] = ob

    # Q11 — avg flight distance by satisfaction
    fd = df.groupby("Satisfaction")["Flight Distance"].mean().round(1).to_dict()
    answers["flight_distance_by_satisfaction"] = fd

    # Q12 — highest / lowest satisfaction customer segment
    # Segment = Customer Type + Type of Travel + Class
    seg = df.groupby(["Customer Type", "Type of Travel", "Class"])["Satisfaction"].apply(
        lambda s: round((s == "Satisfied").mean() * 100, 2)
    ).reset_index()
    seg.columns = ["Customer Type", "Type of Travel", "Class", "Satisfaction Rate (%)"]
    best_seg  = seg.loc[seg["Satisfaction Rate (%)"].idxmax()]
    worst_seg = seg.loc[seg["Satisfaction Rate (%)"].idxmin()]
    answers["best_segment"]  = best_seg.to_dict()
    answers["worst_segment"] = worst_seg.to_dict()

    # Q13 — bottom 3 service areas as improvement opportunities
    answers["bottom_3_services"] = svc.tail(3)["Service"].tolist()

    return answers


# ---------------------------------------------------------------------------
# 10. Dynamic Key Insights Generator
# ---------------------------------------------------------------------------

def generate_key_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate a list of plain-English insight strings calculated from the data.
    Used by the Streamlit dashboard's Key Insights section.
    """
    if df.empty:
        return ["No data available for the current filter selection."]

    insights = []
    kpis = calculate_kpis(df)
    bq   = answer_business_questions(df)

    # Overall satisfaction
    sat_rate = kpis["Satisfaction Rate (%)"]
    insights.append(
        f"📊 **Overall Satisfaction Rate:** {sat_rate:.1f}% of passengers are satisfied "
        f"under the current filter selection."
    )

    # Best customer segment
    ct_sat = bq.get("customer_type_satisfaction", {})
    if ct_sat:
        best_ct  = max(ct_sat, key=ct_sat.get)
        worst_ct = min(ct_sat, key=ct_sat.get)
        insights.append(
            f"👤 **Customer Type:** {best_ct} passengers have a higher satisfaction rate "
            f"({ct_sat[best_ct]:.1f}%) compared to {worst_ct} passengers ({ct_sat[worst_ct]:.1f}%)."
        )

    # Travel type
    tt_sat = bq.get("travel_type_satisfaction", {})
    if tt_sat:
        best_tt  = max(tt_sat, key=tt_sat.get)
        worst_tt = min(tt_sat, key=tt_sat.get)
        insights.append(
            f"✈️ **Travel Type:** {best_tt} travel passengers are more satisfied "
            f"({tt_sat[best_tt]:.1f}%) than {worst_tt} travel passengers ({tt_sat[worst_tt]:.1f}%)."
        )

    # Class
    cl_sat = bq.get("class_satisfaction", {})
    if cl_sat:
        best_cl  = max(cl_sat, key=cl_sat.get)
        worst_cl = min(cl_sat, key=cl_sat.get)
        insights.append(
            f"💺 **Travel Class:** {best_cl} class has the highest satisfaction rate "
            f"({cl_sat[best_cl]:.1f}%) while {worst_cl} class has the lowest "
            f"({cl_sat[worst_cl]:.1f}%)."
        )

    # Best and worst service area
    insights.append(
        f"⭐ **Best Service Area:** '{bq.get('best_service_area', 'N/A')}' "
        f"has the highest average rating ({bq.get('best_service_rating', 0):.2f}/5)."
    )
    insights.append(
        f"⚠️ **Weakest Service Area:** '{bq.get('worst_service_area', 'N/A')}' "
        f"has the lowest average rating ({bq.get('worst_service_rating', 0):.2f}/5) "
        f"and is a key improvement opportunity."
    )

    # Delays
    ds_sat = bq.get("delay_status_satisfaction", {})
    if "On Time" in ds_sat and "Delayed" in ds_sat:
        insights.append(
            f"⏱️ **Delays & Satisfaction:** On-time passengers have a satisfaction rate of "
            f"{ds_sat['On Time']:.1f}%, compared to {ds_sat['Delayed']:.1f}% for delayed passengers."
        )

    # Online boarding
    ob_sat = bq.get("online_boarding_by_satisfaction", {})
    if "Satisfied" in ob_sat and "Neutral or Dissatisfied" in ob_sat:
        insights.append(
            f"📱 **Online Boarding:** Satisfied passengers rate Online Boarding "
            f"{ob_sat['Satisfied']:.2f}/5 on average, vs. "
            f"{ob_sat['Neutral or Dissatisfied']:.2f}/5 for dissatisfied passengers — "
            f"one of the largest differentiating factors."
        )

    return insights


# ---------------------------------------------------------------------------
# 11. Business Recommendations Generator
# ---------------------------------------------------------------------------

def generate_recommendations(df: pd.DataFrame) -> list[dict]:
    """
    Generate data-driven business recommendations.
    Each item is a dict with keys: 'finding', 'recommendation'.
    """
    if df.empty:
        return []

    bq  = answer_business_questions(df)
    kpis = calculate_kpis(df)
    recs = []

    # Rec 1 — weakest service area
    recs.append({
        "finding": (
            f"'{bq.get('worst_service_area', '')}' has the lowest average service rating "
            f"({bq.get('worst_service_rating', 0):.2f}/5) across all passengers."
        ),
        "recommendation": (
            f"The airline should investigate passenger feedback specifically about "
            f"'{bq.get('worst_service_area', '')}' to identify root causes and "
            f"implement targeted service improvements."
        ),
    })

    # Rec 2 — service area with largest satisfaction gap
    recs.append({
        "finding": (
            f"'{bq.get('largest_diff_service', '')}' shows the largest average rating gap "
            f"({bq.get('largest_diff_value', 0):.2f} points) between satisfied and "
            f"dissatisfied passengers."
        ),
        "recommendation": (
            f"Improving '{bq.get('largest_diff_service', '')}' experience could have the "
            f"greatest positive impact on passenger satisfaction rates."
        ),
    })

    # Rec 3 — bottom 3 services
    bottom3 = bq.get("bottom_3_services", [])
    if bottom3:
        recs.append({
            "finding": (
                f"The three lowest-rated service areas are: {', '.join(bottom3)}."
            ),
            "recommendation": (
                "These areas should be prioritised in the airline's service improvement roadmap."
            ),
        })

    # Rec 4 — worst travel class
    cl_sat = bq.get("class_satisfaction", {})
    if cl_sat:
        worst_cl = min(cl_sat, key=cl_sat.get)
        recs.append({
            "finding": (
                f"{worst_cl} class passengers have the lowest satisfaction rate "
                f"({cl_sat[worst_cl]:.1f}%)."
            ),
            "recommendation": (
                f"The airline should review the service offering in {worst_cl} class, "
                f"focusing on the specific service categories that differ most between "
                f"{worst_cl} and higher classes."
            ),
        })

    # Rec 5 — delays
    ds_sat = bq.get("delay_status_satisfaction", {})
    if "On Time" in ds_sat and "Delayed" in ds_sat:
        diff = ds_sat["On Time"] - ds_sat["Delayed"]
        recs.append({
            "finding": (
                f"Delayed passengers have a satisfaction rate {diff:.1f} percentage points "
                f"lower than on-time passengers ({ds_sat['Delayed']:.1f}% vs "
                f"{ds_sat['On Time']:.1f}%)."
            ),
            "recommendation": (
                "Reducing departure and arrival delays — and improving how delays are "
                "communicated to passengers — could meaningfully improve overall satisfaction."
            ),
        })

    # Rec 6 — first-time passengers
    ct_sat = bq.get("customer_type_satisfaction", {})
    if "First-time" in ct_sat:
        recs.append({
            "finding": (
                f"First-time passengers have a satisfaction rate of {ct_sat['First-time']:.1f}%, "
                f"which is lower than Returning passengers ({ct_sat.get('Returning', 0):.1f}%)."
            ),
            "recommendation": (
                "Investing in a better onboarding experience for first-time flyers — "
                "such as clearer guidance on online booking, check-in, and boarding — "
                "could improve first-impression satisfaction and build loyalty."
            ),
        })

    return recs


# ---------------------------------------------------------------------------
# Entry-point: run a quick sanity check when executed directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading and preparing data …")
    df, report = load_and_prepare()
    print(f"Cleaned shape: {df.shape}")
    print("Cleaning report:", report)
    kpis = calculate_kpis(df)
    print("\nKPIs:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
    print("\nService Rating Summary (top 5):")
    print(service_rating_summary(df).head())
    print("\nKey Insights:")
    for ins in generate_key_insights(df):
        print(" •", ins)

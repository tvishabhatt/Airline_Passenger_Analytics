"""
app.py
======
Streamlit Interactive Dashboard
Airline Passenger Experience & Satisfaction Analytics Dashboard

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analysis import (
    load_and_prepare,
    calculate_kpis,
    service_rating_summary,
    service_rating_by_satisfaction,
    satisfaction_by_column,
    satisfaction_distribution,
    delay_summary,
    generate_key_insights,
    generate_recommendations,
    SERVICE_COLS,
    AGE_LABELS,
    DIST_LABELS,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Airline Passenger Satisfaction Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — clean, professional look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-title {font-size: 2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0;}
    .sub-title  {font-size: 1rem; color: #555; margin-top: 0;}
    .kpi-card   {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 16px 18px;
        text-align: center;
        border-left: 4px solid #3b6fd4;
    }
    .kpi-value  {font-size: 1.6rem; font-weight: 700; color: #1a1a2e;}
    .kpi-label  {font-size: 0.78rem; color: #555; margin-top: 4px;}
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a1a2e;
        border-bottom: 2px solid #3b6fd4;
        padding-bottom: 6px;
        margin-top: 10px;
        margin-bottom: 14px;
    }
    .insight-box {
        background: #f7f9ff;
        border-left: 4px solid #3b6fd4;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .finding-box {
        background: #fff8f0;
        border-left: 4px solid #f0a500;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .rec-box {
        background: #f0fff4;
        border-left: 4px solid #28a745;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data (cached so it is read only once per session)
# ---------------------------------------------------------------------------
@st.cache_data
def get_data():
    df, report = load_and_prepare()
    return df, report

df_full, cleaning_report = get_data()

# ---------------------------------------------------------------------------
# SIDEBAR — Filters
# ---------------------------------------------------------------------------
st.sidebar.header("🔍 Filter Passengers")
st.sidebar.markdown("Use the filters below to explore specific passenger segments.")

def multiselect_filter(label, column, df):
    options = sorted(df[column].dropna().unique().tolist())
    return st.sidebar.multiselect(label, options=options, default=options, key=column)

sel_gender       = multiselect_filter("Gender",                "Gender",            df_full)
sel_cust_type    = multiselect_filter("Customer Type",         "Customer Type",     df_full)
sel_travel_type  = multiselect_filter("Type of Travel",        "Type of Travel",    df_full)
sel_class        = multiselect_filter("Class",                 "Class",             df_full)
sel_satisfaction = multiselect_filter("Satisfaction",          "Satisfaction",      df_full)
sel_age_group    = multiselect_filter("Age Group",             "Age Group",         df_full)
sel_delay_status = multiselect_filter("Delay Status",          "Delay Status",      df_full)
sel_dist_cat     = multiselect_filter("Distance Category",     "Distance Category", df_full)

# Apply filters
df = df_full[
    df_full["Gender"].isin(sel_gender) &
    df_full["Customer Type"].isin(sel_cust_type) &
    df_full["Type of Travel"].isin(sel_travel_type) &
    df_full["Class"].isin(sel_class) &
    df_full["Satisfaction"].isin(sel_satisfaction) &
    df_full["Age Group"].isin(sel_age_group) &
    df_full["Delay Status"].isin(sel_delay_status) &
    df_full["Distance Category"].isin(sel_dist_cat)
].copy()

st.sidebar.markdown("---")
st.sidebar.info(f"**Filtered:** {len(df):,} passengers  \n**Total:** {len(df_full):,} passengers")

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown('<p class="main-title">✈️ Airline Passenger Experience & Satisfaction Dashboard</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-title">Interactive analysis of passenger satisfaction, service quality, '
            'travel patterns and flight delays.</p>', unsafe_allow_html=True)
st.markdown("---")

# ---------------------------------------------------------------------------
# Empty-data guard
# ---------------------------------------------------------------------------
if df.empty:
    st.warning("⚠️ No data matches the current filter selection. Please adjust the sidebar filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------------------------
kpis = calculate_kpis(df)

def kpi_card(label, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>"""

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
cards = [
    ("Total Passengers",       f"{kpis['Total Passengers']:,}"),
    ("Satisfied",              f"{kpis['Satisfied Passengers']:,}"),
    ("Satisfaction Rate",      f"{kpis['Satisfaction Rate (%)']:.1f}%"),
    ("Avg Age",                f"{kpis['Average Age']:.1f} yrs"),
    ("Avg Flight Distance",    f"{kpis['Average Flight Distance']:,.0f} km"),
    ("Avg Total Delay",        f"{kpis['Average Total Delay']:.1f} min"),
    ("Avg Service Rating",     f"{kpis['Average Service Rating']:.2f}/5"),
]
for col, (label, value) in zip([col1,col2,col3,col4,col5,col6,col7], cards):
    col.markdown(kpi_card(label, value), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# TABS for dashboard sections
# ============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📋 Passenger Overview",
    "😊 Satisfaction Analysis",
    "⭐ Service Quality",
    "⏱️ Delay Analysis",
    "✈️ Flight Distance",
    "🔍 Key Insights",
    "💡 Recommendations",
    "📄 Data Explorer",
])

# ============================================================================
# TAB 1 — Passenger Overview
# ============================================================================
with tab1:
    st.markdown('<div class="section-header">Passenger Overview</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # Satisfaction distribution
    with c1:
        sat_dist = satisfaction_distribution(df)
        fig = px.pie(
            sat_dist, values="Count", names="Satisfaction",
            title="Overall Satisfaction Distribution",
            color="Satisfaction",
            color_discrete_map={
                "Satisfied": "#3b82f6",
                "Neutral or Dissatisfied": "#f87171",
            },
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # Class distribution
    with c2:
        class_counts = df["Class"].value_counts().reset_index()
        class_counts.columns = ["Class", "Count"]
        fig = px.bar(
            class_counts, x="Class", y="Count",
            title="Passengers by Travel Class",
            color="Class",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    # Customer type distribution
    with c3:
        ct_counts = df["Customer Type"].value_counts().reset_index()
        ct_counts.columns = ["Customer Type", "Count"]
        fig = px.pie(
            ct_counts, values="Count", names="Customer Type",
            title="Customer Type Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # Travel type distribution
    with c4:
        tt_counts = df["Type of Travel"].value_counts().reset_index()
        tt_counts.columns = ["Type of Travel", "Count"]
        fig = px.pie(
            tt_counts, values="Count", names="Type of Travel",
            title="Type of Travel Distribution",
            color_discrete_sequence=px.colors.qualitative.Set1,
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    # Age distribution
    st.markdown('<div class="section-header">Age Distribution</div>', unsafe_allow_html=True)
    fig = px.histogram(
        df, x="Age", color="Satisfaction",
        nbins=40, barmode="overlay",
        title="Age Distribution by Satisfaction",
        color_discrete_map={
            "Satisfied": "#3b82f6",
            "Neutral or Dissatisfied": "#f87171",
        },
        opacity=0.75,
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2 — Satisfaction Analysis
# ============================================================================
with tab2:
    st.markdown('<div class="section-header">Satisfaction Analysis</div>', unsafe_allow_html=True)

    def satisfaction_bar(df, column, title):
        """Helper: grouped bar chart of satisfaction counts by column."""
        grp = df.groupby([column, "Satisfaction"]).size().reset_index(name="Count")
        fig = px.bar(
            grp, x=column, y="Count", color="Satisfaction",
            barmode="group", title=title,
            color_discrete_map={
                "Satisfied": "#3b82f6",
                "Neutral or Dissatisfied": "#f87171",
            },
        )
        return fig

    def satisfaction_rate_bar(df, column, title):
        """Helper: satisfaction rate bar chart."""
        sat_df = satisfaction_by_column(df, column)
        fig = px.bar(
            sat_df, x=column, y="Satisfaction Rate (%)",
            title=title,
            color="Satisfaction Rate (%)",
            color_continuous_scale="Blues",
            text="Satisfaction Rate (%)",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        return fig

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(satisfaction_rate_bar(df, "Customer Type",
                        "Satisfaction Rate by Customer Type"), use_container_width=True)
    with c2:
        st.plotly_chart(satisfaction_rate_bar(df, "Type of Travel",
                        "Satisfaction Rate by Type of Travel"), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(satisfaction_rate_bar(df, "Class",
                        "Satisfaction Rate by Travel Class"), use_container_width=True)
    with c4:
        st.plotly_chart(satisfaction_rate_bar(df, "Gender",
                        "Satisfaction Rate by Gender"), use_container_width=True)

    # Age Group
    st.markdown('<div class="section-header">Satisfaction by Age Group</div>', unsafe_allow_html=True)
    age_order = [a for a in AGE_LABELS if a in df["Age Group"].unique()]
    age_sat = df.groupby(["Age Group", "Satisfaction"]).size().reset_index(name="Count")
    fig = px.bar(
        age_sat, x="Age Group", y="Count", color="Satisfaction",
        barmode="group", title="Satisfaction Count by Age Group",
        category_orders={"Age Group": age_order},
        color_discrete_map={
            "Satisfied": "#3b82f6",
            "Neutral or Dissatisfied": "#f87171",
        },
    )
    st.plotly_chart(fig, use_container_width=True)

    # Delay Status
    st.markdown('<div class="section-header">Satisfaction by Delay Status</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(satisfaction_rate_bar(df, "Delay Status",
                        "Satisfaction Rate: On Time vs Delayed"), use_container_width=True)
    with c6:
        st.plotly_chart(satisfaction_bar(df, "Delay Status",
                        "Passenger Counts: On Time vs Delayed"), use_container_width=True)

# ============================================================================
# TAB 3 — Service Quality
# ============================================================================
with tab3:
    st.markdown('<div class="section-header">Service Quality Analysis</div>', unsafe_allow_html=True)

    # Average service rating bar chart
    svc_summary = service_rating_summary(df)
    fig = px.bar(
        svc_summary.sort_values("Average Rating"),
        x="Average Rating", y="Service",
        orientation="h",
        title="Average Rating per Service Area (Filtered Passengers)",
        color="Average Rating",
        color_continuous_scale="RdYlGn",
        range_color=[1, 5],
        text="Average Rating",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(yaxis_title="", xaxis_range=[0, 5.5], coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # Service rating: Satisfied vs Dissatisfied
    st.markdown('<div class="section-header">Service Ratings: Satisfied vs Neutral/Dissatisfied</div>',
                unsafe_allow_html=True)
    svc_diff = service_rating_by_satisfaction(df)

    fig2 = go.Figure()
    if "Satisfied" in svc_diff.columns:
        fig2.add_trace(go.Bar(
            name="Satisfied",
            x=svc_diff["Service"], y=svc_diff["Satisfied"],
            marker_color="#3b82f6",
        ))
    if "Neutral or Dissatisfied" in svc_diff.columns:
        fig2.add_trace(go.Bar(
            name="Neutral or Dissatisfied",
            x=svc_diff["Service"], y=svc_diff["Neutral or Dissatisfied"],
            marker_color="#f87171",
        ))
    fig2.update_layout(
        barmode="group",
        title="Service Ratings: Satisfied vs Neutral/Dissatisfied Passengers",
        xaxis_tickangle=-35,
        yaxis_title="Average Rating",
        yaxis_range=[0, 5],
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Rating difference heatmap-style table
    st.markdown('<div class="section-header">Rating Gap (Satisfied – Neutral/Dissatisfied)</div>',
                unsafe_allow_html=True)
    diff_display = svc_diff[["Service", "Satisfied", "Neutral or Dissatisfied", "Difference"]].copy()
    diff_display = diff_display.sort_values("Difference", ascending=False)

    fig3 = px.bar(
        diff_display,
        x="Difference", y="Service",
        orientation="h",
        title="Rating Gap: Satisfied minus Neutral/Dissatisfied",
        color="Difference",
        color_continuous_scale="RdBu",
        text="Difference",
    )
    fig3.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig3.update_layout(yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    # Best and Worst callout
    col_best, col_worst = st.columns(2)
    with col_best:
        best_row = svc_summary.iloc[0]
        st.success(f"🏆 **Best Service Area:** {best_row['Service']}  \n"
                   f"Average Rating: **{best_row['Average Rating']:.2f}/5**")
    with col_worst:
        worst_row = svc_summary.iloc[-1]
        st.error(f"⚠️ **Weakest Service Area:** {worst_row['Service']}  \n"
                 f"Average Rating: **{worst_row['Average Rating']:.2f}/5**")

# ============================================================================
# TAB 4 — Delay Analysis
# ============================================================================
with tab4:
    st.markdown('<div class="section-header">Flight Delay Analysis</div>', unsafe_allow_html=True)

    d_summary = delay_summary(df)
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.metric("Avg Departure Delay", f"{d_summary.get('avg_departure_delay', 0):.1f} min")
    dc2.metric("Avg Arrival Delay",   f"{d_summary.get('avg_arrival_delay', 0):.1f} min")
    dc3.metric("Avg Total Delay",     f"{d_summary.get('avg_total_delay', 0):.1f} min")
    dc4.metric("On-Time Rate",        f"{d_summary.get('pct_on_time', 0):.1f}%")

    c1, c2 = st.columns(2)

    with c1:
        # Departure delay distribution (capped at 300 min for readability)
        dep_cap = df[df["Departure Delay"] <= 300]["Departure Delay"]
        fig = px.histogram(
            dep_cap, nbins=60,
            title="Departure Delay Distribution (≤ 300 min)",
            labels={"value": "Departure Delay (min)", "count": "Passengers"},
            color_discrete_sequence=["#3b82f6"],
        )
        fig.update_layout(xaxis_title="Departure Delay (min)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Arrival delay distribution (capped at 300 min)
        arr_cap = df[df["Arrival Delay"] <= 300]["Arrival Delay"]
        fig = px.histogram(
            arr_cap, nbins=60,
            title="Arrival Delay Distribution (≤ 300 min)",
            labels={"value": "Arrival Delay (min)", "count": "Passengers"},
            color_discrete_sequence=["#f87171"],
        )
        fig.update_layout(xaxis_title="Arrival Delay (min)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    # Total delay by satisfaction
    st.markdown('<div class="section-header">Total Delay by Satisfaction</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        avg_delay_by_sat = df.groupby("Satisfaction")["Total Delay"].mean().reset_index()
        avg_delay_by_sat.columns = ["Satisfaction", "Avg Total Delay (min)"]
        fig = px.bar(
            avg_delay_by_sat, x="Satisfaction", y="Avg Total Delay (min)",
            title="Average Total Delay by Satisfaction",
            color="Satisfaction",
            color_discrete_map={
                "Satisfied": "#3b82f6",
                "Neutral or Dissatisfied": "#f87171",
            },
            text="Avg Total Delay (min)",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.pie(
            names=["On Time", "Delayed"],
            values=[d_summary.get("pct_on_time", 0), d_summary.get("pct_delayed", 0)],
            title="On-Time vs Delayed (% of passengers)",
            color_discrete_map={"On Time": "#3b82f6", "Delayed": "#f87171"},
            hole=0.4,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 5 — Flight Distance
# ============================================================================
with tab5:
    st.markdown('<div class="section-header">Flight Distance Analysis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(
            df, x="Flight Distance", nbins=60,
            title="Flight Distance Distribution",
            color_discrete_sequence=["#3b82f6"],
            labels={"Flight Distance": "Flight Distance (km)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        dist_order = [d for d in DIST_LABELS if d in df["Distance Category"].unique()]
        dist_sat = satisfaction_by_column(df, "Distance Category")
        fig = px.bar(
            dist_sat, x="Distance Category", y="Satisfaction Rate (%)",
            title="Satisfaction Rate by Distance Category",
            category_orders={"Distance Category": dist_order},
            color="Satisfaction Rate (%)",
            color_continuous_scale="Blues",
            text="Satisfaction Rate (%)",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Box plot: flight distance by satisfaction
    fig = px.box(
        df, x="Satisfaction", y="Flight Distance",
        title="Flight Distance Distribution by Satisfaction",
        color="Satisfaction",
        color_discrete_map={
            "Satisfied": "#3b82f6",
            "Neutral or Dissatisfied": "#f87171",
        },
        points=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Distance category breakdown table
    st.markdown('<div class="section-header">Satisfaction by Distance Category (Details)</div>',
                unsafe_allow_html=True)
    dist_details = satisfaction_by_column(df, "Distance Category")
    st.dataframe(
        dist_details.style.format({"Satisfaction Rate (%)": "{:.2f}%", "Satisfied": "{:,}", "Total": "{:,}"}),
        use_container_width=True,
    )

# ============================================================================
# TAB 6 — Key Insights
# ============================================================================
with tab6:
    st.markdown('<div class="section-header">Key Insights (Calculated from Filtered Data)</div>',
                unsafe_allow_html=True)
    insights = generate_key_insights(df)
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

    # Summary table
    st.markdown('<div class="section-header">Satisfaction Rate Summary Table</div>',
                unsafe_allow_html=True)
    for col_name, label in [
        ("Customer Type",    "Customer Type"),
        ("Type of Travel",   "Type of Travel"),
        ("Class",            "Travel Class"),
        ("Gender",           "Gender"),
        ("Delay Status",     "Delay Status"),
        ("Distance Category","Distance Category"),
    ]:
        if col_name in df.columns:
            sat_tbl = satisfaction_by_column(df, col_name)
            sat_tbl.rename(columns={col_name: label}, inplace=True)
            with st.expander(f"Satisfaction Rate by {label}"):
                st.dataframe(
                    sat_tbl.style.format({
                        "Satisfaction Rate (%)": "{:.2f}%",
                        "Satisfied": "{:,}",
                        "Total": "{:,}",
                    }),
                    use_container_width=True,
                )

# ============================================================================
# TAB 7 — Business Recommendations
# ============================================================================
with tab7:
    st.markdown('<div class="section-header">Data-Driven Business Recommendations</div>',
                unsafe_allow_html=True)
    st.markdown(
        "The following recommendations are derived strictly from the analysis of the filtered "
        "dataset. Each recommendation is paired with its supporting data finding.",
        unsafe_allow_html=False,
    )

    recs = generate_recommendations(df)
    for i, rec in enumerate(recs, 1):
        st.markdown(f"**Recommendation {i}**", unsafe_allow_html=False)
        st.markdown(
            f'<div class="finding-box"><strong>DATA FINDING:</strong> {rec["finding"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="rec-box"><strong>BUSINESS RECOMMENDATION:</strong> {rec["recommendation"]}</div>',
            unsafe_allow_html=True,
        )

# ============================================================================
# TAB 8 — Data Explorer
# ============================================================================
with tab8:
    st.markdown('<div class="section-header">Filtered Passenger Data</div>', unsafe_allow_html=True)
    st.write(f"Showing **{len(df):,}** passengers matching the current filter selection.")

    # Column selection
    display_cols = st.multiselect(
        "Select columns to display",
        options=df.columns.tolist(),
        default=[
            "ID", "Gender", "Age", "Customer Type", "Type of Travel", "Class",
            "Flight Distance", "Total Delay", "Avg Service Rating", "Satisfaction",
            "Age Group", "Distance Category", "Delay Status",
        ],
    )
    if display_cols:
        st.dataframe(df[display_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

    # Download button
    @st.cache_data
    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode("utf-8")

    csv_bytes = convert_df_to_csv(df)
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_passengers.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("**Data Cleaning Summary**")
    cr = cleaning_report
    st.write({
        "Original Rows":               cr.get("original_rows", "N/A"),
        "Duplicate Rows Found":        cr.get("duplicates_found", "N/A"),
        "Missing Arrival Delay Rows":  cr.get("missing_arrival_delay", "N/A"),
        "Arrival Delay Fill Value":    cr.get("arrival_delay_fill_value", "N/A"),
        "Invalid Rows Removed":        cr.get("invalid_rows_removed", "N/A"),
        "Final Rows":                  cr.get("final_rows", "N/A"),
    })

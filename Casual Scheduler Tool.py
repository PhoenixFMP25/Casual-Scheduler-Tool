import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_costs(weekly_hours):
    """
    Calculate the total cost of employing a worker as a full-time vs casual based on weekly hours,
    including the possibility of switching from casual to full-time mid-period.
    """
    hourly_cost_full_time = 122.37  # Updated Full-Time hourly rate
    hourly_cost_casual = 132.53  # Updated Casual hourly rate
    full_time_hours_per_week = 40  # Full-time employees are always paid for 40 hours per week
    
    total_hours = sum(weekly_hours)
    total_weeks_worked = sum(1 for h in weekly_hours if h > 0)
    full_time_costs = [full_time_hours_per_week * hourly_cost_full_time for _ in weekly_hours]
    casual_costs = [h * hourly_cost_casual for h in weekly_hours]
    full_time_total = sum(full_time_costs[:total_weeks_worked])
    casual_total = sum(casual_costs[:total_weeks_worked])
    
    # Determine the best week to switch to full-time based on cost efficiency
    best_switch_week = None
    best_switch_cost = float('inf')
    for week in range(2, total_weeks_worked + 1):
        switch_full_time_costs = [
            full_time_hours_per_week * hourly_cost_full_time if i >= week - 1 else h * hourly_cost_casual
            for i, h in enumerate(weekly_hours[:total_weeks_worked])
        ]
        switch_total = sum(switch_full_time_costs)
        if switch_total < best_switch_cost:
            best_switch_week = week
            best_switch_cost = switch_total
    
    return total_hours, total_weeks_worked, full_time_total, casual_total, best_switch_week, best_switch_cost, full_time_costs[:total_weeks_worked], casual_costs[:total_weeks_worked]

# Streamlit App
st.title("Casual Scheduler Tool")

weeks = 8  # Define maximum number of weeks

# Initialize session state for reset functionality
if "weekly_hours" not in st.session_state:
    st.session_state.weekly_hours = [0] * weeks

def reset_inputs():
    st.session_state.weekly_hours = [0] * weeks
    st.rerun()

# Labour Cost Workings Button at the Top of Sidebar
if st.sidebar.button("Labour Cost Workings"):
    breakdown_data = {
        "Pay Item": ["Base Rate", "Payroll Tax", "Superannuation", "Annual Leave", "Annual Leave Loading", "Sick Leave", "Public Holidays", "Incolink", "LeavePlus/CoInvest", "Workers Compensation", "Compliance Training", "Uniforms/PPE", "Training", "Fares & Travel", "Device Allowance", "Overhead Fee"],
        "Full-Time Cost ($)": [71.81, 5.01, 8.26, 6.30, 0.10, 3.15, 3.78, 5.29, 1.94, 2.15, 3.00, 0.63, 2.06, 4.80, 0.50, 3.59],
        "Casual Cost ($)": [89.76, 5.33, 10.32, 0.00, 0.00, 0.00, 0.00, 6.51, 2.42, 2.69, 3.00, 0.63, 2.06, 4.80, 0.50, 4.49]
    }
    breakdown_df = pd.DataFrame(breakdown_data)
    breakdown_df.loc["Total"] = breakdown_df.sum(numeric_only=True)
    breakdown_df.loc["Total", "Pay Item"] = "Total"
    st.subheader("Labour Cost Breakdown as of 1st February 2025")
    st.dataframe(breakdown_df)

total_weeks_selected = 0
st.sidebar.header("Input Work Schedule")
st.sidebar.write("Select the number of **days** worked per week")

weekly_hours = []
for i in range(weeks):
    if i == 0 or (i > 0 and weekly_hours[i - 1] > 0):  # Only show next week if previous week has a selection
        days = st.sidebar.radio(f"Week {i+1}:", options=[0, 1, 2, 3, 4, 5], index=st.session_state.weekly_hours[i] // 8, horizontal=True, key=f"week_{i}")
        weekly_hours.append(days * 8)  # Convert days to hours
        st.session_state.weekly_hours[i] = days * 8  # Update session state
        if days > 0:
            total_weeks_selected += 1
    else:
        weekly_hours.append(0)  # Append 0 for hidden weeks

if st.sidebar.button("Calculate Costs"):
    total_hours, total_weeks_worked, full_time_total, casual_total, best_switch_week, best_switch_cost, full_time_costs, casual_costs = calculate_costs(weekly_hours[:total_weeks_selected])

    st.subheader("Scheduling Summary")
    st.write(f"**{total_weeks_worked} Weeks Worked / Total Hours:** {total_hours}")
    st.write(f"**Equivalent Full-Time Cost:** ${full_time_total:,.2f}")
    st.write(f"**Equivalent Casual Cost:** ${casual_total:,.2f}")
    
    if best_switch_week:
        st.write(f"**Recommended Equivalent Cost:** ${best_switch_cost:,.2f}")

# Recommendation Wording
    if best_switch_week:
        st.write(f"**Recommendation:** Move to Full Time after Week {best_switch_week - 1}")
        st.write("**Comments:**")
        st.write(f"Moving to full-time after Week {best_switch_week - 1} provides the best cost efficiency. From Week {best_switch_week} onward, full-time rates will apply, reducing overall costs compared to staying casual.")
    else:
        st.write(f"**Recommendation:** Leave on Casual for all {total_weeks_selected} weeks.")
        st.write("**Comments:**")
        st.write(f"Remaining casual for all {total_weeks_selected} weeks is the most cost-effective approach. A switch to full-time does not provide significant financial benefit in this scenario.")    
    
# Cost Comparison Graph
    st.subheader("Cost Comparison: Full-Time vs. Casual")
    fig, ax = plt.subplots()
    bars = ["Full-Time", "Casual"]
    costs = [full_time_total, casual_total]
    sns.barplot(x=bars, y=costs, ax=ax, palette=["black", "red"])
    for i, v in enumerate(costs):
        ax.text(i, v + (0.02 * max(costs)), f"${v:,.2f}", ha='center', fontsize=10, fontweight='bold')
    st.pyplot(fig)
    
# Recommendation Graph
    if best_switch_week:
        st.subheader(f"Recommendation: Full-Time from Week {best_switch_week} vs. Casual")
        fig, ax = plt.subplots()
        bars = [f"Full-Time from Week {best_switch_week}", "Casual"]
        costs = [best_switch_cost, casual_total]
        sns.barplot(x=bars, y=costs, ax=ax, palette=["black", "red"])
        for i, v in enumerate(costs):
            ax.text(i, v + (0.02 * max(costs)), f"${v:,.2f}", ha='center', fontsize=10, fontweight='bold')
        st.pyplot(fig)
    
# Week-by-Week Cost Breakdown
    worked_weeks = [i+1 for i in range(total_weeks_selected)]
    pay_table = pd.DataFrame({
        "Week": worked_weeks,
        "Casual Cost ($)": casual_costs,
        "Full-Time Cost ($)": full_time_costs,
        "Recommendation ($)": [
            casual_costs[i] if best_switch_week and i + 1 < best_switch_week else full_time_costs[i]
            for i in range(total_weeks_selected)
        ],
        "Comments": [
            "Moved to Full-Time" if best_switch_week and i + 1 == best_switch_week else ""
            for i in range(total_weeks_selected)
        ]
    })
    st.subheader("Week-by-Week Cost Breakdown")
    st.dataframe(pay_table)

if st.sidebar.button("Reset to Default"):
    reset_inputs()

# Code Revision: v2.45






































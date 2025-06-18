# CPU Scheduling Visualizer with Multiple Algorithms and Features

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="🧠 CPU Scheduling Visualizer", layout="wide")
st.title("🧠 CPU Scheduling Visualizer")

# --- Sidebar Inputs ---
st.sidebar.header("Input Configuration")
num_processes = st.sidebar.number_input("Number of processes", min_value=1, max_value=10, step=1)
algorithm = st.sidebar.selectbox("Select Scheduling Algorithm", ["FCFS", "SJF", "Round Robin", "Priority"])
time_quantum = 1

if algorithm == "Round Robin":
    time_quantum = st.sidebar.number_input("Time Quantum (RR)", min_value=1, step=1)

# --- Process Data Input ---
st.subheader("Enter Process Details")
process_data = []

for i in range(num_processes):
    with st.expander(f"Process P{i+1}"):
        bt = st.number_input(f"Burst Time for P{i+1}", min_value=1, key=f"bt{i}")
        pr = st.number_input(f"Priority for P{i+1} (Lower = Higher Priority)", min_value=1, key=f"pr{i}") if algorithm == "Priority" else 0
        process_data.append({"Process": f"P{i+1}", "Burst Time": bt, "Priority": pr})

# --- Function Definitions ---
def fcfs_scheduling(data):
    df = pd.DataFrame(data)
    df["Start Time"] = df["Burst Time"].cumsum() - df["Burst Time"]
    df["Completion Time"] = df["Burst Time"].cumsum()
    df["Turnaround Time"] = df["Completion Time"]
    df["Waiting Time"] = df["Turnaround Time"] - df["Burst Time"]
    return df

def sjf_scheduling(data):
    df = pd.DataFrame(sorted(data, key=lambda x: x["Burst Time"]))
    return fcfs_scheduling(df.to_dict('records'))

def priority_scheduling(data):
    df = pd.DataFrame(sorted(data, key=lambda x: x["Priority"]))
    return fcfs_scheduling(df.to_dict('records'))

def round_robin_scheduling(data, quantum):
    queue = data.copy()
    time_elapsed = 0
    result = []
    ready_queue = []
    index = 0
    while any(p['Burst Time'] > 0 for p in queue):
        p = queue[index % len(queue)]
        if p['Burst Time'] > 0:
            exec_time = min(quantum, p['Burst Time'])
            result.append({"Process": p['Process'], "Start Time": time_elapsed, "Duration": exec_time})
            time_elapsed += exec_time
            p['Burst Time'] -= exec_time
        index += 1
    return result

def visualize_gantt(df, rr_mode=False):
    fig, gnt = plt.subplots(figsize=(10, 2))
    gnt.set_ylim(0, 50)
    gnt.set_xlim(0, df["Completion Time"].max() + 2 if not rr_mode else df[-1]["Start Time"] + df[-1]["Duration"])
    gnt.set_xlabel("Time")
    gnt.set_yticks([])
    gnt.set_title("Gantt Chart")

    if not rr_mode:
        for i in range(len(df)):
            gnt.broken_barh([(df["Start Time"][i], df["Burst Time"][i])], (10, 9), facecolors="skyblue")
            gnt.text(df["Start Time"][i] + df["Burst Time"][i]/2 - 0.5, 12, df["Process"][i], color='black')
    else:
        for p in df:
            gnt.broken_barh([(p['Start Time'], p['Duration'])], (10, 9), facecolors="lightcoral")
            gnt.text(p['Start Time'] + p['Duration']/2 - 0.5, 12, p['Process'], color='black')
    st.pyplot(fig)

# --- Main Execution ---
if st.button("🔁 Run Scheduling"):
    if algorithm == "FCFS":
        df_result = fcfs_scheduling(process_data)
        st.dataframe(df_result)
        visualize_gantt(df_result)

    elif algorithm == "SJF":
        df_result = sjf_scheduling(process_data)
        st.dataframe(df_result)
        visualize_gantt(df_result)

    elif algorithm == "Priority":
        df_result = priority_scheduling(process_data)
        st.dataframe(df_result)
        visualize_gantt(df_result)

    elif algorithm == "Round Robin":
        rr_result = round_robin_scheduling(process_data, time_quantum)
        st.write(pd.DataFrame(rr_result))
        visualize_gantt(rr_result, rr_mode=True)

    # Export Option
    if algorithm != "Round Robin":
        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download as CSV", csv, "scheduling_results.csv", "text/csv")

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os
import plotly.express as px

st.set_page_config(page_title="LeetCode Tracker", page_icon="💻", layout="wide")

FILE_NAME = "leetcode_progress.csv"

COLUMNS = [
    "Date",
    "Problem",
    "Number",
    "Difficulty",
    "Topic",
    "Status",
    "Time Spent",
    "Confidence",
    "Link",
    "Notes",
    "Last Reviewed"
]

DIFFICULTY_XP = {
    "Easy": 10,
    "Medium": 25,
    "Hard": 50
}

TOPICS = [
    "Array",
    "Hash Map",
    "Two Pointers",
    "Sliding Window",
    "Binary Search",
    "Stack",
    "Queue",
    "Linked List",
    "Tree",
    "Graph",
    "Dynamic Programming",
    "Greedy",
    "Backtracking",
    "Other"
]

STATUSES = ["Not Started", "Attempted", "Solved", "Need Review"]

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=COLUMNS)

for col in COLUMNS:
    if col not in df.columns:
        df[col] = ""

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Last Reviewed"] = pd.to_datetime(df["Last Reviewed"], errors="coerce")
df["Time Spent"] = pd.to_numeric(df["Time Spent"], errors="coerce").fillna(0)
df["Confidence"] = pd.to_numeric(df["Confidence"], errors="coerce").fillna(0)

st.title("💻 LeetCode Tracker Dashboard")

with st.sidebar:
    st.header("Add New Problem")

    problem = st.text_input("Problem Name")
    number = st.text_input("Problem Number")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    topic = st.selectbox("Topic", TOPICS)
    status = st.selectbox("Status", STATUSES)
    time_spent = st.number_input("Time Spent (minutes)", min_value=0, step=5)
    confidence = st.slider("Confidence", 1, 5, 3)
    link = st.text_input("LeetCode Link")
    notes = st.text_area("Notes")

    if st.button("Add Problem"):
        if problem.strip() == "":
            st.error("Enter a problem name first.")
        else:
            new_problem = {
                "Date": date.today(),
                "Problem": problem,
                "Number": number,
                "Difficulty": difficulty,
                "Topic": topic,
                "Status": status,
                "Time Spent": time_spent,
                "Confidence": confidence,
                "Link": link,
                "Notes": notes,
                "Last Reviewed": date.today() if status == "Solved" else ""
            }

            df = pd.concat([df, pd.DataFrame([new_problem])], ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            st.success("Problem added successfully!")
            st.rerun()

total = len(df)
solved_df = df[df["Status"] == "Solved"]
solved = len(solved_df)
attempted = len(df[df["Status"] == "Attempted"])
review = len(df[df["Status"] == "Need Review"])

total_xp = solved_df["Difficulty"].map(DIFFICULTY_XP).fillna(0).sum()
level = int(total_xp // 100) + 1
xp_in_level = int(total_xp % 100)

st.subheader("📊 Overall Stats")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Problems", total)
col2.metric("Solved", solved)
col3.metric("Attempted", attempted)
col4.metric("Need Review", review)

st.subheader("🏆 XP and Level")

xp_col1, xp_col2, xp_col3 = st.columns(3)

xp_col1.metric("Total XP", int(total_xp))
xp_col2.metric("Level", level)
xp_col3.metric("XP to Next Level", 100 - xp_in_level)

st.progress(xp_in_level / 100)

st.divider()

st.subheader("🔥 Streak Tracker")

if solved > 0:
    solved_dates = solved_df["Date"].dropna().dt.date.unique()
    solved_dates = sorted(solved_dates)

    today = date.today()
    current_streak = 0
    check_day = today

    while check_day in solved_dates:
        current_streak += 1
        check_day -= timedelta(days=1)

    best_streak = 1
    temp_streak = 1

    for i in range(1, len(solved_dates)):
        if solved_dates[i] == solved_dates[i - 1] + timedelta(days=1):
            temp_streak += 1
            best_streak = max(best_streak, temp_streak)
        else:
            temp_streak = 1

    streak_col1, streak_col2 = st.columns(2)
    streak_col1.metric("Current Streak", f"{current_streak} days")
    streak_col2.metric("Best Streak", f"{best_streak} days")
else:
    st.info("Solve a problem to start your streak.")

st.divider()

colA, colB = st.columns(2)

with colA:
    st.subheader("Difficulty Breakdown")
    if total > 0:
        difficulty_counts = df["Difficulty"].value_counts().reset_index()
        difficulty_counts.columns = ["Difficulty", "Count"]

        fig = px.bar(
            difficulty_counts,
            x="Difficulty",
            y="Count",
            text="Count",
            title="Problems by Difficulty"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No problems yet.")

with colB:
    st.subheader("Topic Breakdown")
    if total > 0:
        topic_counts = df["Topic"].value_counts().reset_index()
        topic_counts.columns = ["Topic", "Count"]

        fig = px.bar(
            topic_counts,
            x="Topic",
            y="Count",
            text="Count",
            title="Problems by Topic"
        )

        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No topics yet.")

st.divider()

st.subheader("📈 Progress Over Time")

if solved > 0:
    progress_df = solved_df.copy()
    progress_df["Date"] = progress_df["Date"].dt.date

    daily_solved = progress_df.groupby("Date").size().reset_index(name="Solved Problems")
    daily_solved["Total Solved"] = daily_solved["Solved Problems"].cumsum()

    fig = px.line(
        daily_solved,
        x="Date",
        y="Total Solved",
        markers=True,
        title="Total Solved Problems Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Mark problems as solved to see progress over time.")

st.divider()

st.subheader("🧠 Weakest Topics")

if total > 0:
    topic_summary = df.groupby("Topic").agg(
        Total=("Problem", "count"),
        Solved=("Status", lambda x: (x == "Solved").sum()),
        Need_Review=("Status", lambda x: (x == "Need Review").sum()),
        Average_Confidence=("Confidence", "mean")
    ).reset_index()

    topic_summary["Solve Rate"] = round((topic_summary["Solved"] / topic_summary["Total"]) * 100, 1)
    topic_summary = topic_summary.sort_values(by=["Solve Rate", "Average_Confidence"])

    st.dataframe(topic_summary, use_container_width=True)
else:
    st.info("Add problems to see your weakest topics.")

st.divider()

st.subheader("🔍 Filter Problems")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    difficulty_filter = st.selectbox("Filter by Difficulty", ["All", "Easy", "Medium", "Hard"])

with filter_col2:
    status_filter = st.selectbox("Filter by Status", ["All"] + STATUSES)

with filter_col3:
    topic_filter = st.selectbox("Filter by Topic", ["All"] + sorted(df["Topic"].dropna().unique().tolist()))

filtered_df = df.copy()

if difficulty_filter != "All":
    filtered_df = filtered_df[filtered_df["Difficulty"] == difficulty_filter]

if status_filter != "All":
    filtered_df = filtered_df[filtered_df["Status"] == status_filter]

if topic_filter != "All":
    filtered_df = filtered_df[filtered_df["Topic"] == topic_filter]

st.dataframe(filtered_df, use_container_width=True)

st.divider()

st.subheader("🔗 Clickable Problem Links")

links_df = df[df["Link"].notna() & (df["Link"] != "")]

if len(links_df) > 0:
    for _, row in links_df.iterrows():
        st.markdown(f"- [{row['Problem']}]({row['Link']})")
else:
    st.info("Add LeetCode links to see clickable links here.")

st.divider()

st.subheader("📝 Update Problem Status")

if total > 0:
    selected_problem = st.selectbox("Select a problem", df["Problem"].tolist())
    new_status = st.selectbox("New Status", STATUSES)

    if st.button("Update Status"):
        df.loc[df["Problem"] == selected_problem, "Status"] = new_status

        if new_status == "Solved":
            df.loc[df["Problem"] == selected_problem, "Last Reviewed"] = date.today()

        df.to_csv(FILE_NAME, index=False)
        st.success("Status updated!")
        st.rerun()
else:
    st.info("Add a problem first.")

st.divider()

st.subheader("📚 Problems That Need Review")

review_df = df[df["Status"] == "Need Review"]

if len(review_df) > 0:
    st.dataframe(review_df, use_container_width=True)
else:
    st.success("No review problems right now.")

st.divider()

st.subheader("⬇️ Download Your Data")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="leetcode_progress.csv",
    mime="text/csv"
)
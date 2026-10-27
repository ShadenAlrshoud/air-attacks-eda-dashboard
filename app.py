import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- Page setup ----------------
st.set_page_config(page_title="Air Attacks Dashboard", layout="wide")

# Dark style for the matplotlib charts, to match the dark theme of the app
BG = "#0E1117"
plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.edgecolor": "#555555",
    "axes.labelcolor": "#FAFAFA",
    "xtick.color": "#FAFAFA",
    "ytick.color": "#FAFAFA",
    "text.color": "#FAFAFA",
    "axes.grid": True,
    "grid.color": "#333333",
    "axes.axisbelow": True,
})
BLUE, RED, GREEN = "#4C9BE8", "#E63946", "#2A9D8F"


@st.cache_data
def load_data():
    df = pd.read_csv("clean_data.csv")
    df["start_time"] = pd.to_datetime(df["start_time"])
    return df


df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title("About the Data")
st.sidebar.markdown(
    """
    This dashboard explores the **Russian missile and drone attacks on Ukraine**
    (September 2022 – October 2026), based on the official daily reports of the
    **Ukrainian Air Force**.

    Each record is one attack with one weapon model, showing how many weapons were
    **launched** and how many were **destroyed** by air defense.

    **Source:** [Kaggle: Massive Missile Attacks on Ukraine](https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine)
    """
)

st.sidebar.header("Filters")

# Slider: year range
min_year, max_year = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("Year range", min_year, max_year, (min_year, max_year))

# Dropdown: weapon type
weapon_type = st.sidebar.selectbox("Weapon type", ["All weapons", "Shahed drones only", "Other weapons only"])

# Multiselect: weapon models (empty = all)
model_list = df["weapon_model"].value_counts().index.tolist()
selected_models = st.sidebar.multiselect(
    "Weapon models (leave empty for all)", model_list, default=[]
)

# Slider: attack size
max_size = int(df["launched"].max())
size_range = st.sidebar.slider("Attack size (number launched)", 1, max_size, (1, max_size))

# ---------------- Apply filters ----------------
filtered = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

if weapon_type == "Shahed drones only":
    filtered = filtered[filtered["is_shahed"]]
elif weapon_type == "Other weapons only":
    filtered = filtered[~filtered["is_shahed"]]

if selected_models:
    filtered = filtered[filtered["weapon_model"].isin(selected_models)]

filtered = filtered[(filtered["launched"] >= size_range[0]) & (filtered["launched"] <= size_range[1])]

# ---------------- Main page ----------------
st.title("Air Attacks & Air Defense Dashboard")
st.markdown(
    "Explore how air attacks have changed over time, which weapons are the hardest to intercept, "
    "and whether large attacks overwhelm air defense. Use the **filters in the sidebar** to explore the data."
)

if filtered.empty:
    st.warning("No data matches the selected filters. Try changing the filters in the sidebar.")
    st.stop()

# Key numbers
total_launched = filtered["launched"].sum()
total_destroyed = filtered["destroyed"].sum()
rate = total_destroyed / total_launched * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Attack records", f"{len(filtered):,}")
col2.metric("Weapons launched", f"{total_launched:,}")
col3.metric("Weapons destroyed", f"{total_destroyed:,}")
col4.metric("Interception rate", f"{rate:.1f}%")

st.caption("Interception rate = total destroyed ÷ total launched × 100")

# Data preview & summary statistics
with st.expander("Data preview"):
    st.dataframe(filtered.head(100), use_container_width=True)

with st.expander("Summary statistics"):
    st.dataframe(filtered[["launched", "destroyed", "interception_rate"]].describe().round(2),
                 use_container_width=True)

# ---------------- Charts ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Over Time", "Weapons", "Attack Size", "Days & Months", "Shahed Drones"])

# --- Tab 1: Over time ---
with tab1:
    st.subheader("Weapons launched and destroyed per month")
    monthly = filtered.set_index("start_time").resample("ME")[["launched", "destroyed"]].sum()
    st.line_chart(monthly, color=[BLUE, RED])

    st.subheader("Interception rate per year")
    yearly = filtered.groupby("year")[["launched", "destroyed"]].sum()
    yearly["interception_rate"] = (yearly["destroyed"] / yearly["launched"] * 100).round(1)
    st.dataframe(yearly, use_container_width=True)

    st.info("💡The scale of attacks grew enormously, from about 1,200 weapons in 2022 to more than "
            "74,000 in 2026. The interception rate dropped to about 68% in 2024–2025, then rose to almost 89% in 2026.")

# --- Tab 2: Weapons ---
with tab2:
    left, right = st.columns(2)

    with left:
        st.subheader("Top 10 weapon models by total launched")
        top_models = filtered.groupby("weapon_model")["launched"].sum().sort_values().tail(10)
        fig, ax = plt.subplots(figsize=(6, 5))
        top_models.plot(kind="barh", ax=ax, color=BLUE)
        ax.set_xlabel("Total launched")
        ax.set_ylabel("")
        st.pyplot(fig)

    with right:
        st.subheader("Interception rate by weapon model")
        min_attacks = st.slider("Minimum number of attacks per model", 1, 100, 50)
        stats = filtered.groupby("weapon_model").agg(
            attacks=("weapon_model", "size"),
            launched=("launched", "sum"),
            destroyed=("destroyed", "sum"))
        stats = stats[stats["attacks"] >= min_attacks]

        if stats.empty:
            st.write("No weapon model has that many attacks with the current filters.")
        else:
            stats["interception_rate"] = stats["destroyed"] / stats["launched"] * 100
            stats = stats.sort_values("interception_rate")
            fig, ax = plt.subplots(figsize=(6, 5))
            stats["interception_rate"].plot(kind="barh", ax=ax, color=RED)
            ax.set_xlabel("Interception rate (%)")
            ax.set_ylabel("")
            st.pyplot(fig)

    st.info("💡Shahed drones are by far the most used weapon. Ballistic missiles such as Iskander-M "
            "and C-300 are the hardest to intercept, while most other drones are intercepted at almost 100%.")

# --- Tab 3: Attack size ---
with tab3:
    st.markdown("**Attack size** = the number of weapons launched in one attack record.")
    left, right = st.columns(2)

    with left:
        st.subheader("Interception rate by attack size")
        sized = filtered.copy()
        sized["attack_size"] = pd.cut(sized["launched"], bins=[0, 5, 20, 50, 100, 1000],
                                      labels=["1-5", "6-20", "21-50", "51-100", "100+"])
        size_stats = sized.groupby("attack_size", observed=True)[["launched", "destroyed"]].sum()
        size_stats["interception_rate"] = size_stats["destroyed"] / size_stats["launched"] * 100

        fig, ax = plt.subplots(figsize=(6, 4))
        size_stats["interception_rate"].plot(kind="bar", ax=ax, color=RED)
        ax.set_ylabel("Interception rate (%)")
        ax.set_xlabel("Attack size")
        ax.tick_params(axis="x", rotation=0)
        st.pyplot(fig)

    with right:
        st.subheader("Attack size vs interception rate")
        st.scatter_chart(filtered, x="launched", y="interception_rate")
        st.caption("Each dot is one attack. Hover over a dot to see its values.")

    st.info("💡Large attacks are not intercepted at a lower rate. The lowest rate is for small attacks "
            "(1–5 weapons), which are often single ballistic missiles. The type of weapon matters more than the size.")

# --- Tab 4: Days & months ---
with tab4:
    left, right = st.columns(2)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    with left:
        st.subheader("Number of attacks by day of week")
        days = filtered["day_of_week"].value_counts().reindex(day_order, fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 4))
        days.plot(kind="bar", ax=ax, color=BLUE)
        ax.set_ylabel("Number of attacks")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig)

    with right:
        st.subheader("Total weapons launched by month")
        months = filtered.groupby("month")["launched"].sum().reindex(range(1, 13), fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 4))
        months.plot(kind="bar", ax=ax, color=GREEN)
        ax.set_ylabel("Total launched")
        ax.set_xlabel("Month")
        ax.tick_params(axis="x", rotation=0)
        st.pyplot(fig)

    st.info("💡Attacks are spread almost evenly across the days of the week. The monthly totals are mostly "
            "shaped by the growth over the years.")

# --- Tab 5: Shahed drones ---
with tab5:
    st.subheader("Share of Shahed drones per year")
    shahed = filtered.groupby(["year", "is_shahed"])["launched"].sum().unstack(fill_value=0)
    shahed = shahed.rename(columns={True: "Shahed", False: "Other weapons"})
    colors = {"Other weapons": GREEN, "Shahed": RED}
    st.bar_chart(shahed, color=[colors[c] for c in shahed.columns])

    if "Shahed" in shahed.columns:
        share = (shahed["Shahed"] / shahed.sum(axis=1) * 100).round(1)
        st.dataframe(share.rename("Shahed share (%)"), use_container_width=True)

    st.info("💡Shahed drones grew from 35% of all weapons in 2022 to 93% in 2025. In 2024–2025, thousands "
            "of Shaheds were reported as lost to electronic warfare rather than destroyed, which partly explains "
            "the lower interception rate in those years.")

# ---------------- Key insights ----------------
st.markdown("---")
st.header("Key Insights")
st.markdown(
    """
    * **The air war grew dramatically**: from about 1,200 weapons launched in 2022 to more than 74,000 in 2026.
    * **It became mainly a drone war**: Shahed drones made up as much as 93% of all weapons launched.
    * **Weapon type decides the interception rate**: ballistic missiles are very hard to stop, while most drones are intercepted.
    * **Large attacks do not overwhelm air defense**: attacks of 100+ weapons still had about 79% interception.
    * Overall, about **79% of all weapons were intercepted**.
    """
)
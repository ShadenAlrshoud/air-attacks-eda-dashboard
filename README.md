# Air Attacks & Air Defense: Data Exploration & Dashboard

**Author:** Shaden

An exploratory data analysis (EDA) of the Russian missile and drone attacks on Ukraine (September 2022 – October 2026),
with an interactive Streamlit dashboard.

## Why this project
Missile and drone attacks are not just a news topic for us. Here in Riyadh, we are currently living with these threats, which made me want to understand them through data.
My first goal was to analyze real data about the attacks here on Saudi Arabia, but detailed public data about them (such as the number of weapons launched and intercepted) is not available.
So I chose this dataset, because it is one of the most detailed real and publicly available records of air attacks: it is based on official daily reports and covers four years of attacks with the same kinds of weapons, such as drones and ballistic missiles.
By studying it, I want to learn patterns that can also apply to our situation: how attacks grow, which weapons are the hardest to intercept, and whether large attacks overwhelm air defense.
These insights can help us better understand the challenges that air defense faces, and how can our country prepare for similar threats.

## Dataset
* **Massive Missile Attacks on Ukraine** (Kaggle, by Petro Ivaniuk):
  https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine
* Based on the official daily reports of the Ukrainian Air Force.

## Project files
| File | Description |
|---|---|
| `EDA_project.ipynb` | Jupyter Notebook: data loading, cleaning, EDA and insights |
| `clean_data.csv` | Cleaned dataset used by the dashboard |
| `app.py` | Streamlit dashboard |
| `requirements.txt` | Python libraries needed |
| `.streamlit/config.toml` | Dark theme settings for the dashboard |

The interactive Streamlit dashboard is live at: air-attacks-eda-dashboard.streamlit.app and lets anyone explore the data with filters, without installing anything.

## How to run the dashboard
1. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
2. Make sure `app.py`, `clean_data.csv` and the `.streamlit` folder are in the same folder.
3. Run:
   ```
   streamlit run app.py
   ```
4. The dashboard opens in your browser at `http://localhost:8501`.


## Dashboard features
* **Sidebar:** dataset description and filters (year range slider, weapon type dropdown, weapon models multiselect, attack size slider)
* **Key numbers:** attack records, weapons launched, weapons destroyed, interception rate
* **Data preview** and **summary statistics**
* **Interactive charts** in 5 tabs: over time, weapons, attack size, days & months, Shahed drones
* **Insight sections** under each chart and a key insights summary

## Key insights
* The number of weapons launched grew from about 1,200 in 2022 to more than 74,000 in 2026.
* Shahed drones made up as much as 93% of all weapons launched.
* Ballistic missiles are the hardest to intercept, while most drones are intercepted at almost 100%.
* Large attacks do not lower the interception rate: the type of weapon matters more than the size.
* Overall, about 79% of all weapons were intercepted.

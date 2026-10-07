import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

# Run this script with the repository root as the working directory.
data_file = "C:/Users/olive/OneDrive/Desktop/Python Programming 2 course/COP_3045_2026_Fall_Team_4/03_Data_Cleaning/clean_data.csv"

output_dir = "C:/Users/olive/OneDrive/Desktop/Python Programming 2 course/COP_3045_2026_Fall_Team_4/05-Report"

df = pd.read_csv(data_file)

row_count = len(df)
column_count = len(df.columns)
years = df["posted_year"].dropna().sort_values()
first_year = years.min()
last_year = years.max()
country_count = df["country"].nunique()
title_count = df["standardized_title"].nunique()
experience_level_count = df["experience_level"].nunique()
remote_type_count = df["remote_type"].nunique()

summary_statistics = df[
    ["min_experience_years", "salary_min_usd", "salary_max_usd"]
].agg(["mean", "min", "median", "max"]).T

title_counts = df["standardized_title"].value_counts().sort_values(ascending=True)

plt.figure(figsize=(12, max(5, min(12, len(title_counts) * 0.3))))
sns.barplot(x=title_counts.values, y=title_counts.index.astype(str), color="steelblue")
plt.title("Job Postings by Standardized Job Title")
plt.xlabel("Number of postings")
plt.ylabel("Standardized job title")
plt.tight_layout()
plt.savefig(output_dir + "/standardized_title_postings.png", dpi=200, bbox_inches="tight")
plt.close()

experience_values = df["experience_level"].dropna().unique().tolist()
experience_order = []
for level in ["Entry", "Mid", "Senior"]:
    if level in experience_values:
        experience_order.append(level)
for level in experience_values:
    if level not in experience_order:
        experience_order.append(level)

plt.figure(figsize=(10, 6))
sns.boxplot(
    data=df,
    x="experience_level",
    y="salary_max_usd",
    order=experience_order,
    color="lightblue",
)
plt.title("Upper Salary Bound by Experience Level")
plt.xlabel("Experience level")
plt.ylabel("Upper salary bound (USD)")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(output_dir + "/salary_by_experience_level.png", dpi=200, bbox_inches="tight")
plt.close()

remote_arrangements = df["remote_type"].dropna()
remote_arrangements = remote_arrangements[
    remote_arrangements.astype(str).str.strip() != ""
]
remote_counts = remote_arrangements.value_counts().sort_values(ascending=True)

plt.figure(figsize=(9, 6))
sns.barplot(
    x=remote_counts.index.astype(str),
    y=remote_counts.values,
    color="seagreen",
)
plt.title("Job Postings by Work Arrangement")
plt.xlabel("Work arrangement")
plt.ylabel("Number of postings")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(output_dir + "/work_arrangement_distribution.png", dpi=200, bbox_inches="tight")
plt.close()

year_counts = df.groupby("posted_year").size().sort_index()

plt.figure(figsize=(10, 6))
sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o", color="darkorange")
plt.title("Job Postings by Year")
plt.xlabel("Posted year")
plt.ylabel("Number of postings")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(output_dir + "/job_postings_by_year.png", dpi=200, bbox_inches="tight")
plt.close()

most_frequent_title_count = title_counts.max()
most_frequent_titles = title_counts[
    title_counts == most_frequent_title_count
].index.tolist()
most_frequent_titles_text = ", ".join(str(title) for title in most_frequent_titles)

salary_by_experience = (
    df.dropna(subset=["experience_level", "salary_max_usd"])
    .groupby("experience_level")["salary_max_usd"]
    .mean()
)
highest_mean_salary = salary_by_experience.max()
highest_salary_levels = salary_by_experience[
    salary_by_experience == highest_mean_salary
].index.tolist()
highest_salary_levels_text = ", ".join(
    str(level) for level in highest_salary_levels
)

most_common_remote_count = remote_counts.max()
most_common_remote_types = remote_counts[
    remote_counts == most_common_remote_count
].index.tolist()
most_common_remote_types_text = ", ".join(
    str(remote_type) for remote_type in most_common_remote_types
)
remote_percentage = most_common_remote_count / len(remote_arrangements) * 100

year_highest_count = year_counts.max()
highest_posting_years = year_counts[
    year_counts == year_highest_count
].index.tolist()
highest_posting_years_text = ", ".join(
    str(year) for year in highest_posting_years
)

skills_nonblank = df["skills"].notna() & (df["skills"].astype(str).str.strip() != "")
skills_count = int(skills_nonblank.sum())
skills_percentage = skills_count / row_count * 100

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_title("AI Job Market Analysis")
pdf.set_author("Automated dataset report")
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.multi_cell(
    0,
    10,
    "AI Job Market Analysis: Roles, Salaries, Experience, and Work Arrangements",
)
pdf.ln(2)

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Dataset Summary", ln=1)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, f"Observations: {row_count:,}")
pdf.multi_cell(0, 6, f"Variables: {column_count:,}")
pdf.multi_cell(0, 6, f"Years represented: {first_year} to {last_year}")
pdf.multi_cell(0, 6, f"Countries represented: {country_count:,}")
pdf.multi_cell(0, 6, f"Standardized job titles: {title_count:,}")
pdf.multi_cell(0, 6, f"Experience levels: {experience_level_count:,}")
pdf.multi_cell(0, 6, f"Work arrangement categories: {remote_type_count:,}")
pdf.multi_cell(
    0,
    6,
    f"Rows with nonblank skills: {skills_count:,} ({skills_percentage:.1f}% of all rows).",
)
pdf.ln(3)

pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Summary Statistics", ln=1)
pdf.set_font("Helvetica", size=9)
pdf.cell(75, 8, "Measure", border=1, align="C")
pdf.cell(26.25, 8, "Mean", border=1, align="C")
pdf.cell(26.25, 8, "Minimum", border=1, align="C")
pdf.cell(26.25, 8, "Median", border=1, align="C")
pdf.cell(26.25, 8, "Maximum", border=1, align="C", ln=1)

for measure in summary_statistics.index:
    if measure == "min_experience_years":
        measure_label = "Minimum experience (years)"
    elif measure == "salary_min_usd":
        measure_label = "Salary range lower bound (USD)"
    else:
        measure_label = "Salary range upper bound (USD)"
    pdf.cell(75, 8, measure_label, border=1)
    for statistic in ["mean", "min", "median", "max"]:
        value = summary_statistics.loc[measure, statistic]
        if measure == "min_experience_years":
            value_text = f"{value:,.1f}"
        else:
            value_text = f"USD {value:,.0f}"
        pdf.cell(26.25, 8, value_text, border=1, align="C")
    pdf.ln(8)

pdf.ln(3)
pdf.set_font("Helvetica", size=9)
pdf.multi_cell(
    0,
    5,
    "Salary minimum and maximum are the listed lower and upper bounds of the posted range; they are not actual earned salaries.",
)

pdf.add_page()
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Job Postings by Standardized Job Title", ln=1)
pdf.image(output_dir + "/standardized_title_postings.png", x=15, y=35, w=180)

pdf.add_page()
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Upper Salary Bound by Experience Level", ln=1)
pdf.image(output_dir + "/salary_by_experience_level.png", x=15, y=35, w=180)

pdf.add_page()
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Job Postings by Work Arrangement", ln=1)
pdf.image(output_dir + "/work_arrangement_distribution.png", x=15, y=35, w=180)

pdf.add_page()
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Job Postings by Year", ln=1)
pdf.image(output_dir + "/job_postings_by_year.png", x=15, y=35, w=180)

pdf.add_page()
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "Key Findings", ln=1)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(
    0,
    7,
    f"Most frequent standardized title(s): {most_frequent_titles_text} ({most_frequent_title_count:,} postings).",
)
pdf.ln(2)
pdf.multi_cell(
    0,
    7,
    f"Experience level(s) with the highest mean upper salary bound: {highest_salary_levels_text} (USD {highest_mean_salary:,.0f}).",
)
pdf.ln(2)
pdf.multi_cell(
    0,
    7,
    f"Most common work arrangement(s): {most_common_remote_types_text} ({most_common_remote_count:,} postings; {remote_percentage:.1f}% of postings with a nonblank work arrangement).",
)
pdf.ln(2)
pdf.multi_cell(
    0,
    7,
    f"Year(s) with the most postings: {highest_posting_years_text} ({year_highest_count:,} postings).",
)
pdf.ln(5)
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Limitations", ln=1)
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(
    0,
    6,
    "Posting frequencies and annual counts describe this dataset, not verified total market demand or employment growth. The dataset does not establish market representativeness or causation, and does not confirm whether the latest year is complete.",
)

pdf.output(output_dir + "/project_report.pdf")

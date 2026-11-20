"""Generate the report's four original charts without changing their design."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_standardized_titles(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot posting counts by standardized title."""
    try:
        title_counts = df["standardized_title"].value_counts().sort_values(ascending=True)

        plt.figure(figsize=(12, max(5, min(12, len(title_counts) * 0.3))))
        sns.barplot(x=title_counts.values, y=title_counts.index.astype(str), color="steelblue")
        plt.title("Job Postings by Standardized Job Title")
        plt.xlabel("Number of postings")
        plt.ylabel("Standardized job title")
        plt.tight_layout()
        plt.savefig(str(output_dir / "standardized_title_postings.png"), dpi=200, bbox_inches="tight")
        return output_dir / "standardized_title_postings.png"
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(
            f"Could not generate chart {output_dir}/standardized_title_postings.png: {error}"
        ) from error
    finally:
        plt.close()


def plot_salary_by_experience(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot upper salary bounds using the original experience ordering."""
    try:
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
        plt.savefig(str(output_dir / "salary_by_experience_level.png"), dpi=200, bbox_inches="tight")
        return output_dir / "salary_by_experience_level.png"
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(
            f"Could not generate chart {output_dir}/salary_by_experience_level.png: {error}"
        ) from error
    finally:
        plt.close()


def plot_work_arrangements(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot counts of nonblank work arrangements."""
    try:
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
        plt.savefig(str(output_dir / "work_arrangement_distribution.png"), dpi=200, bbox_inches="tight")
        return output_dir / "work_arrangement_distribution.png"
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(
            f"Could not generate chart {output_dir}/work_arrangement_distribution.png: {error}"
        ) from error
    finally:
        plt.close()


def plot_postings_by_year(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot posting counts in chronological order."""
    try:
        year_counts = df.groupby("posted_year").size().sort_index()

        plt.figure(figsize=(10, 6))
        sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o", color="darkorange")
        plt.title("Job Postings by Year")
        plt.xlabel("Posted year")
        plt.ylabel("Number of postings")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(str(output_dir / "job_postings_by_year.png"), dpi=200, bbox_inches="tight")
        return output_dir / "job_postings_by_year.png"
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(
            f"Could not generate chart {output_dir}/job_postings_by_year.png: {error}"
        ) from error
    finally:
        plt.close()


def generate_charts(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Write all four report charts to an existing output directory."""
    return [
        plot_standardized_titles(df, output_dir),
        plot_salary_by_experience(df, output_dir),
        plot_work_arrangements(df, output_dir),
        plot_postings_by_year(df, output_dir),
    ]

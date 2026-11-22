"""Unified visualization module for both EDA and automated PDF reporting."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _validate_chart_inputs(
    df: pd.DataFrame, required_columns: list[str], output_dir: Path
) -> Path:
    """Validate DataFrame columns and ensure output directory exists."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("Input data must be a non-empty pandas DataFrame.")

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {missing}")

    resolved_dir = Path(output_dir)
    resolved_dir.mkdir(parents=True, exist_ok=True)
    return resolved_dir


def plot_standardized_titles(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot posting counts by standardized title."""
    out_dir = _validate_chart_inputs(df, ["standardized_title"], output_dir)
    out_path = out_dir / "standardized_title_postings.png"
    try:
        title_counts = df["standardized_title"].value_counts().sort_values(ascending=True)

        plt.figure(figsize=(12, max(5, min(12, len(title_counts) * 0.3))))
        sns.barplot(x=title_counts.values, y=title_counts.index.astype(str), color="steelblue")
        plt.title("Job Postings by Standardized Job Title")
        plt.xlabel("Number of postings")
        plt.ylabel("Standardized job title")
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def plot_salary_by_experience(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot upper salary bounds using the original experience ordering."""
    out_dir = _validate_chart_inputs(df, ["experience_level", "salary_max_usd"], output_dir)
    out_path = out_dir / "salary_by_experience_level.png"
    try:
        experience_values = df["experience_level"].dropna().unique().tolist()
        experience_order = [
            lvl for lvl in ["Entry", "Mid", "Senior"] if lvl in experience_values
        ]
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
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def plot_work_arrangements(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot counts of nonblank work arrangements."""
    out_dir = _validate_chart_inputs(df, ["remote_type"], output_dir)
    out_path = out_dir / "work_arrangement_distribution.png"
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
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def plot_postings_by_year(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot posting counts in chronological order."""
    out_dir = _validate_chart_inputs(df, ["posted_year"], output_dir)
    out_path = out_dir / "job_postings_by_year.png"
    try:
        year_counts = df.groupby("posted_year").size().sort_index()

        plt.figure(figsize=(10, 6))
        sns.lineplot(x=year_counts.index, y=year_counts.values, marker="o", color="darkorange")
        plt.title("Job Postings by Year")
        plt.xlabel("Posted year")
        plt.ylabel("Number of postings")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def plot_salary_range_by_experience(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot minimum vs. maximum salary across experience levels."""
    out_dir = _validate_chart_inputs(
        df, ["experience_level", "salary_min_usd", "salary_max_usd"], output_dir
    )
    out_path = out_dir / "salary_range_by_experience.png"
    try:
        df_melted = df.melt(
            id_vars=["experience_level"],
            value_vars=["salary_min_usd", "salary_max_usd"],
            var_name="Salary Type",
            value_name="Salary (USD)",
        )
        df_melted["Salary Type"] = df_melted["Salary Type"].replace(
            {"salary_min_usd": "Min Salary", "salary_max_usd": "Max Salary"}
        )

        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=df_melted,
            x="experience_level",
            y="Salary (USD)",
            hue="Salary Type",
            order=["Entry", "Mid", "Senior"],
            palette="Set2",
        )
        plt.title("Salary Range (Min vs. Max) Across Experience Levels", fontsize=14, pad=15)
        plt.xlabel("Experience Level", fontsize=12)
        plt.ylabel("Salary (USD)", fontsize=12)
        plt.legend(title="Metric")
        sns.despine()
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def plot_salary_by_years_experience(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot minimum salary distribution by required years of experience."""
    out_dir = _validate_chart_inputs(
        df, ["min_experience_years", "salary_min_usd"], output_dir
    )
    out_path = out_dir / "salary_by_years_experience.png"
    try:
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=df,
            x="min_experience_years",
            y="salary_min_usd",
            hue="min_experience_years",
            palette="Set2",
            legend=False,
        )
        plt.title("Salary Distribution by Required Years of Experience", fontsize=14, pad=15)
        plt.xlabel("Minimum Experience Required (Years)", fontsize=12)
        plt.ylabel("Minimum Salary (USD)", fontsize=12)
        sns.despine()
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def plot_overall_salary_distribution(df: pd.DataFrame, output_dir: Path) -> Path:
    """Plot overall minimum vs. maximum salary frequency and KDE distribution."""
    out_dir = _validate_chart_inputs(
        df, ["salary_min_usd", "salary_max_usd"], output_dir
    )
    out_path = out_dir / "overall_salary_distribution.png"
    try:
        plt.figure(figsize=(11, 6))
        sns.histplot(
            data=df,
            x="salary_min_usd",
            color="teal",
            label="Min Salary",
            kde=True,
            bins=30,
            alpha=0.5,
        )
        sns.histplot(
            data=df,
            x="salary_max_usd",
            color="coral",
            label="Max Salary",
            kde=True,
            bins=30,
            alpha=0.4,
        )
        plt.title("Overall Salary Distribution (Min vs. Max USD)", fontsize=14, pad=15)
        plt.xlabel("Salary (USD)", fontsize=12)
        plt.ylabel("Frequency / Count", fontsize=12)
        plt.legend()
        sns.despine()
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=200, bbox_inches="tight")
        return out_path
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"Could not generate chart {out_path}: {error}") from error
    finally:
        plt.close()


def generate_eda_charts(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Generate and save the three core EDA salary visualizations."""
    return [
        plot_salary_range_by_experience(df, output_dir),
        plot_salary_by_years_experience(df, output_dir),
        plot_overall_salary_distribution(df, output_dir),
    ]


def generate_charts(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Write all four report charts to an existing output directory."""
    return [
        plot_standardized_titles(df, output_dir),
        plot_salary_by_experience(df, output_dir),
        plot_work_arrangements(df, output_dir),
        plot_postings_by_year(df, output_dir),
    ]
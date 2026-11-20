"""Coordinate analysis, charts, and the existing six-page PDF layout."""

from pathlib import Path

from fpdf import FPDF

from .analysis import (
    DatasetSummary, ReportFindings, calculate_findings, calculate_summary, load_data,
)
from .charts import generate_charts


class ReportGenerator:
    """Generate a job-market report using encapsulated input and output paths."""

    def __init__(self, data_file: Path, output_dir: Path) -> None:
        """Store paths without reading data or generating any output."""
        self._data_file = Path(data_file).resolve()
        self._output_dir = Path(output_dir).resolve()

    def generate(self) -> Path:
        """Validate data, generate charts, and return the written PDF path."""
        df = load_data(self._data_file)
        summary = calculate_summary(df)
        findings = calculate_findings(df)
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise RuntimeError(
                f"Could not prepare report output directory '{self._output_dir}': {error}"
            ) from error
        generate_charts(df, self._output_dir)
        try:
            return self._write_pdf(summary, findings)
        except (OSError, ValueError, RuntimeError) as error:
            raise RuntimeError(
                f"Could not generate PDF '{self._output_dir / 'project_report.pdf'}': {error}"
            ) from error

    def _write_pdf(self, summary: DatasetSummary, findings: ReportFindings) -> Path:
        """Write the original text, table, and chart layout using calculated results."""
        output_dir = self._output_dir
        row_count = summary["row_count"]
        column_count = summary["column_count"]
        first_year = summary["first_year"]
        last_year = summary["last_year"]
        country_count = summary["country_count"]
        title_count = summary["title_count"]
        experience_level_count = summary["experience_level_count"]
        remote_type_count = summary["remote_type_count"]
        summary_statistics = summary["summary_statistics"]
        most_frequent_title_count = findings["most_frequent_title_count"]
        most_frequent_titles_text = findings["most_frequent_titles_text"]
        highest_mean_salary = findings["highest_mean_salary"]
        highest_salary_levels_text = findings["highest_salary_levels_text"]
        most_common_remote_count = findings["most_common_remote_count"]
        most_common_remote_types_text = findings["most_common_remote_types_text"]
        remote_percentage = findings["remote_percentage"]
        year_highest_count = findings["year_highest_count"]
        highest_posting_years_text = findings["highest_posting_years_text"]
        skills_count = findings["skills_count"]
        skills_percentage = findings["skills_percentage"]

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
        pdf.image(str(output_dir / "standardized_title_postings.png"), x=15, y=35, w=180)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Upper Salary Bound by Experience Level", ln=1)
        pdf.image(str(output_dir / "salary_by_experience_level.png"), x=15, y=35, w=180)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Job Postings by Work Arrangement", ln=1)
        pdf.image(str(output_dir / "work_arrangement_distribution.png"), x=15, y=35, w=180)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Job Postings by Year", ln=1)
        pdf.image(str(output_dir / "job_postings_by_year.png"), x=15, y=35, w=180)

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

        pdf.output(str(output_dir / "project_report.pdf"))
        return output_dir / "project_report.pdf"

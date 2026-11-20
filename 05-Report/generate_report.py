"""Run automated PDF reporting as the application's seventh stage."""

from pathlib import Path
import sys

from reporting import ReportGenerator


def main() -> None:
    """Generate the report with portable paths and report failures to the caller."""
    output_dir = Path(__file__).resolve().parent
    data_file = output_dir.parent / "03_Data_Cleaning" / "clean_data.csv"
    try:
        report_path = ReportGenerator(data_file, output_dir).generate()
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Reporting failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print(f"PDF report generated: {report_path}")


if __name__ == "__main__":
    main()

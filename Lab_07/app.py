from pathlib import Path

from core import rank_employees, senior_bonus_policy, total_payroll


def run() -> None:
    base_path = Path(__file__).resolve().parent
    json_path = base_path / "sample_data.json"
    csv_path = base_path / "sample_data.csv"

    top_json = rank_employees(json_path, top=5)
    print("Top 5 active employees (JSON, standard bonus policy):")
    for idx, emp in enumerate(top_json, start=1):
        print(
            f"{idx}. {emp.name} | {emp.department} | "
            f"salary={emp.salary:.2f} | bonus={emp.bonus:.2f} | "
            f"total={emp.total_compensation:.2f} | exp={emp.experience} yrs"
        )
    print(f"Total payroll for Top 5: {total_payroll(top_json):.2f}\n")

    top_csv = rank_employees(csv_path, top=3, bonus_fn=senior_bonus_policy)
    print("Top 3 active employees (CSV, senior bonus policy):")
    for idx, emp in enumerate(top_csv, start=1):
        print(
            f"{idx}. {emp.name} | {emp.department} | "
            f"salary={emp.salary:.2f} | bonus={emp.bonus:.2f} | "
            f"total={emp.total_compensation:.2f} | exp={emp.experience} yrs"
        )

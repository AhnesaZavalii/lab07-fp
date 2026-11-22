import io
from functools import partial
from operator import attrgetter, itemgetter, methodcaller
from pathlib import Path

import pytest

from core import (
    calculate_bonus,
    normalize_employee,
    pipeline,
    rank_employees,
    senior_bonus_policy,
    standard_bonus_policy,
    total_payroll,
)
from loaders import load_employees
from models import EmployeeOrder


def test_pipeline_execution() -> None:
    add_two = lambda x: x + 2
    triple = lambda x: x * 3
    assert pipeline(4, add_two, triple) == 18
    assert pipeline(10) == 10


def test_partial_bonus_policies() -> None:
    emp = {
        "name": "Alice",
        "department": "IT",
        "salary": 2000.0,
        "experience": 5,
        "active": True,
    }
    res_std = standard_bonus_policy(emp)
    res_sen = senior_bonus_policy(emp)
    custom = partial(calculate_bonus, base_rate=0.20, exp_step_rate=0.0, max_rate=0.50)
    res_cust = custom(emp)

    assert res_std["bonus"] == 400.0
    assert res_sen["bonus"] == 600.0
    assert res_cust["bonus"] == 400.0


def test_operator_utilities() -> None:
    raw = {
        "name": "  ivan petrenko  ",
        "department": "  QA ",
        "salary": "2500",
        "experience": "2",
        "active": "true",
    }
    norm = normalize_employee(raw)
    assert norm["name"] == "Ivan Petrenko"
    assert norm["department"] == "QA"

    strip_and_upper = lambda s: methodcaller("upper")(methodcaller("strip")(s))
    assert strip_and_upper("  dev  ") == "DEV"

    rows = [{"a": 2, "b": 1}, {"a": 1, "b": 5}, {"a": 1, "b": 2}]
    assert sorted(rows, key=itemgetter("a", "b")) == [
        {"a": 1, "b": 2},
        {"a": 1, "b": 5},
        {"a": 2, "b": 1},
    ]

    emps = [
        EmployeeOrder("B", "IT", 3000, 2, True, 300),
        EmployeeOrder("A", "IT", 4000, 4, True, 400),
    ]
    assert [e.name for e in sorted(emps, key=attrgetter("salary"))] == ["B", "A"]


def test_singledispatch_loaders(tmp_path: Path) -> None:
    records = [
        {"name": "Anna", "department": "IT", "salary": 3000, "experience": 3, "active": True},
        {"name": "Oleh", "department": "QA", "salary": 2500, "experience": 2, "active": False},
    ]
    json_str = '[{"name": "Anna", "department": "IT", "salary": 3000, "experience": 3, "active": true}, {"name": "Oleh", "department": "QA", "salary": 2500, "experience": 2, "active": false}]'
    csv_str = "name,department,salary,experience,active\nAnna,IT,3000,3,true\nOleh,QA,2500,2,false\n"

    json_file = tmp_path / "employees.json"
    json_file.write_text(json_str, encoding="utf-8")

    csv_file = tmp_path / "employees.csv"
    csv_file.write_text(csv_str, encoding="utf-8")

    from_list = load_employees(records)
    from_json_str = load_employees(json_str)
    from_json_path = load_employees(json_file)
    from_json_str_path = load_employees(str(json_file))
    from_csv_path = load_employees(csv_file)
    from_csv_str_path = load_employees(str(csv_file))

    with json_file.open(encoding="utf-8") as jf:
        from_json_stream = load_employees(jf)

    csv_stream = io.StringIO(csv_str)
    from_csv_stream = load_employees(csv_stream)

    assert len(from_list) == 2
    assert from_list == from_json_str == from_json_path == from_json_str_path == from_json_stream
    assert len(from_csv_path) == 2
    assert from_csv_path == from_csv_str_path == from_csv_stream

    with pytest.raises(TypeError):
        load_employees(12345)

def test_total_ordering_comparisons() -> None:
    e1 = EmployeeOrder("Alice", "IT", 3000, 3, True, 300)
    e2 = EmployeeOrder("Bob", "IT", 3000, 5, True, 300)
    e3 = EmployeeOrder("Alice", "HR", 3000, 3, True, 500)
    e4 = EmployeeOrder("Charlie", "IT", 4000, 1, True, 400)

    assert e1 == e3
    assert not (e1 != e3)
    assert e1 < e2
    assert e1 <= e2
    assert e1 <= e3
    assert e4 > e2
    assert e4 >= e2
    assert e3 >= e1
    assert (e1 == "not_employee") is False
    with pytest.raises(TypeError):
        _ = e1 < "not_employee"


def test_rank_employees_pipeline() -> None:
    data = [
        {"name": "  ivan ", "department": "IT", "salary": 3000, "experience": 2, "active": False},
        {"name": "  olena ", "department": "IT", "salary": 4000, "experience": 4, "active": True},
        {"name": "  petro ", "department": "QA", "salary": 3500, "experience": 5, "active": True},
        {"name": "  maria ", "department": "DevOps", "salary": 4500, "experience": 3, "active": True},
    ]
    ranked = rank_employees(data, top=2)
    assert len(ranked) == 2
    assert [e.name for e in ranked] == ["Maria", "Olena"]
    assert total_payroll(ranked) == round(
        ranked[0].total_compensation + ranked[1].total_compensation, 2
    )

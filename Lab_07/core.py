from collections.abc import Callable, Iterable
from functools import partial, reduce
from operator import attrgetter, itemgetter, methodcaller
from typing import Any

from loaders import load_employees
from models import EmployeeOrder

get_name = itemgetter("name")
get_department = itemgetter("department")
get_salary = itemgetter("salary")
get_experience = itemgetter("experience")
get_active = itemgetter("active")

strip_text = methodcaller("strip")
title_text = methodcaller("title")
lower_text = methodcaller("lower")


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    return reduce(lambda acc, fn: fn(acc), funcs, value)


def _to_bool(raw: Any) -> bool:
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return bool(raw)
    if isinstance(raw, str):
        val = lower_text(strip_text(raw))
        if val in {"true", "1", "yes", "y"}:
            return True
        if val in {"false", "0", "no", "n", ""}:
            return False
    raise ValueError(f"Cannot convert active value to bool: {raw!r}")


def normalize_employee(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": title_text(strip_text(str(get_name(record)))),
        "department": strip_text(str(get_department(record))),
        "salary": float(get_salary(record)),
        "experience": int(get_experience(record)),
        "active": _to_bool(get_active(record)),
    }


def calculate_bonus(
    record: dict[str, Any],
    base_rate: float = 0.10,
    exp_step_rate: float = 0.02,
    max_rate: float = 0.35,
) -> dict[str, Any]:
    salary = float(get_salary(record))
    experience = int(get_experience(record))
    rate = min(base_rate + max(experience, 0) * exp_step_rate, max_rate)
    bonus = round(salary * rate, 2)
    return {
        **record,
        "bonus": bonus,
        "total_compensation": round(salary + bonus, 2),
    }


standard_bonus_policy = partial(
    calculate_bonus,
    base_rate=0.10,
    exp_step_rate=0.02,
    max_rate=0.35,
)

senior_bonus_policy = partial(
    calculate_bonus,
    base_rate=0.15,
    exp_step_rate=0.03,
    max_rate=0.45,
)


def mapf(fn: Callable[[Any], Any]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    return partial(map, fn)


def filt(pred: Callable[[Any], bool]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    return partial(filter, pred)


def take_top(n: int) -> Callable[[Iterable[Any]], list[Any]]:
    if n < 0:
        raise ValueError("Parameter 'top' cannot be negative")
    return lambda items: list(items)[:n]


def is_active_employee(record: dict[str, Any]) -> bool:
    return bool(get_active(record))


def to_employee_order(record: dict[str, Any]) -> EmployeeOrder:
    return EmployeeOrder(
        name=str(record["name"]),
        department=str(record["department"]),
        salary=float(record["salary"]),
        experience=int(record["experience"]),
        active=bool(record["active"]),
        bonus=float(record.get("bonus", 0.0)),
    )


def total_payroll(employees: Iterable[EmployeeOrder]) -> float:
    return round(
        reduce(lambda acc, emp: acc + emp.total_compensation, employees, 0.0),
        2,
    )


def rank_employees(
    source: Any,
    top: int = 5,
    bonus_fn: Callable[[dict[str, Any]], dict[str, Any]] = standard_bonus_policy,
) -> list[EmployeeOrder]:
    raw_records = load_employees(source)
    sort_by_rank = partial(
        sorted,
        key=attrgetter("total_compensation", "experience", "name"),
        reverse=True,
    )
    return pipeline(
        raw_records,
        mapf(normalize_employee),
        filt(is_active_employee),
        mapf(bonus_fn),
        mapf(to_employee_order),
        list,
        sort_by_rank,
        take_top(top),
    )

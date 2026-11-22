from functools import total_ordering

@total_ordering
class EmployeeOrder:
    def __init__(
        self,
        name: str,
        department: str,
        salary: float,
        experience: int,
        active: bool = True,
        bonus: float = 0.0,
    ) -> None:
        self.name = name
        self.department = department
        self.salary = float(salary)
        self.experience = int(experience)
        self.active = bool(active)
        self.bonus = float(bonus)

    @property
    def total_compensation(self) -> float:
        return round(self.salary + self.bonus, 2)

    def _sort_key(self) -> tuple[float, int, str]:
        return (self.salary, self.experience, self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EmployeeOrder):
            return NotImplemented
        return self._sort_key() == other._sort_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, EmployeeOrder):
            return NotImplemented
        return self._sort_key() < other._sort_key()

    def __repr__(self) -> str:
        return (
            f"EmployeeOrder(name={self.name!r}, department={self.department!r}, "
            f"salary={self.salary}, experience={self.experience}, "
            f"active={self.active}, bonus={self.bonus})"
        )

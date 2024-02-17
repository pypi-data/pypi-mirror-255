from dataclasses import dataclass


@dataclass
class Task:
    file: str
    func: str
    args: tuple
    kwargs: dict

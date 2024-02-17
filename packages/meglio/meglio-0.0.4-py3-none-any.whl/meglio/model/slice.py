from dataclasses import dataclass, field
from typing import List


@dataclass
class Slice:
    id: int
    ts: int
    dur: int
    name: str
    parent_id: int = None

    parent: "Slice" = None
    children: List["Slice"] = field(default_factory=lambda: [])

    end_ts: int = None
    self_dur: int = None

    def __iter__(self):
        for slice in self.children:
            yield slice

    def compute_end_ts(self):
        self.end_ts = self.ts + self.dur

    def compute_self_dur(self):
        self.self_dur = self.dur
        for child in self.children:
            child.compute_self_dur()
            self.self_dur -= child.self_dur

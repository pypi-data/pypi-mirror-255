from dataclasses import dataclass
from typing import Dict, List

from perfetto.trace_processor import TraceProcessor

from .slice import Slice


@dataclass
class SliceSet:
    """
    A set of `Slice`.
    """

    slices: List[Slice]
    id_index: Dict[int, Slice] = None
    name_index: Dict[str, List[Slice]] = None
    root: Slice = None

    @classmethod
    def from_query(cls, tp: TraceProcessor, query: str, optimize=False) -> "SliceSet":
        slices: List[Slice] = []

        for row in tp.query(query):
            slice = Slice(
                id=row.id,
                ts=row.ts,
                dur=row.dur,
                name=row.name,
                parent_id=row.parent_id,
            )
            slices.append(slice)

        slice_set = SliceSet(slices=slices)
        if optimize:
            slice_set.optimize()
        return slice_set

    def optimize(self):
        self.index_id()
        self.index_name()
        self.construct_tree()
        self.root.compute_self_dur()

    def index_id(self):
        self.id_index = {}
        for slice in self.slices:
            self.id_index[slice.id] = slice

    def index_name(self):
        self.name_index = {}
        for slice in self.slices:
            if slice.name in self.name_index:
                self.name_index[slice.name].append(slice)
            else:
                self.name_index[slice.name] = [slice]

    def construct_tree(self):
        self.root = Slice(id=-1, ts=-1, dur=-1, name="root")
        for slice in self.slices:
            if slice.parent_id is not None and slice.parent_id in self.id_index:
                slice.parent = self.id_index[slice.parent_id]
                slice.parent.children.append(slice)
            else:
                slice.parent = self.root
                self.root.children.append(slice)

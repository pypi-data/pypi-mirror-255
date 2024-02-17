from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set

from meglio.model import Slice, SliceSet


class MergeStrategy(Enum):
    UNIONIZED = 1
    INTERSECTED = 2


@dataclass
class StatisticalMethodDiff:
    name: str
    slices: List[Slice] = field(default_factory=lambda: [])

    avg_dur: float = None
    total_dur: int = None
    self_dur: int = None
    avg_self_dur: float = None

    def compute_dur(self):
        self.total_dur = sum([s.dur for s in self.slices])
        self.self_dur = sum([s.self_dur for s in self.slices])
        self.avg_dur = self.total_dur / len(self.slices)
        self.avg_self_dur = self.self_dur / len(self.slices)


@dataclass
class StatisticalDiffResult:
    added_methods: List[StatisticalMethodDiff] = field(default_factory=lambda: [])
    removed_methods: List[StatisticalMethodDiff] = field(default_factory=lambda: [])


def __get_unionized_and_intersected_names(slice_sets: List[SliceSet]):
    unionized_names = {s.name for s in slice_sets[0].slices}
    intersected_names = {s.name for s in slice_sets[0].slices}

    for slice_set in slice_sets[1:]:
        names = {s.name for s in slice_set.slices}
        unionized_names = unionized_names.union(names)
        intersected_names = intersected_names.intersection(names)

    return unionized_names, intersected_names


def __get_diffs(slice_set: SliceSet, names: Set[str]):
    method_diffs: List[StatisticalMethodDiff] = []

    for name in names:
        method_diff = StatisticalMethodDiff(
            name=name,
            slices=slice_set.name_index[name],
        )
        method_diff.slices.sort(key=lambda s: s.dur, reverse=True)
        method_diff.compute_dur()
        method_diffs.append(method_diff)

    method_diffs.sort(key=lambda diff: diff.self_dur, reverse=True)
    return method_diffs


def statistical_diff(
    base_slice_sets: List[SliceSet],
    target_slice_sets: List[SliceSet],
    minuend_merge_strategy: MergeStrategy = MergeStrategy.INTERSECTED,
    subtrahend_merge_strategy: MergeStrategy = MergeStrategy.UNIONIZED,
):
    base_unionized_names, base_intersected_names = (
        __get_unionized_and_intersected_names(base_slice_sets)
    )
    target_unionized_names, target_intersected_names = (
        __get_unionized_and_intersected_names(target_slice_sets)
    )

    base_map = {
        MergeStrategy.UNIONIZED: base_unionized_names,
        MergeStrategy.INTERSECTED: base_intersected_names,
    }

    target_map = {
        MergeStrategy.UNIONIZED: target_unionized_names,
        MergeStrategy.INTERSECTED: target_intersected_names,
    }

    minuend = target_map[minuend_merge_strategy]
    subtrahend = base_map[subtrahend_merge_strategy]

    added_methods = minuend - subtrahend

    minuend = base_map[minuend_merge_strategy]
    subtrahend = target_map[subtrahend_merge_strategy]

    removed_methods = minuend - subtrahend

    return StatisticalDiffResult(
        added_methods=__get_diffs(target_slice_sets[0], added_methods),
        removed_methods=__get_diffs(base_slice_sets[0], removed_methods),
    )

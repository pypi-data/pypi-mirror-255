from dataclasses import dataclass


@dataclass
class CpuSchedSlice:
    id: int
    ts: int
    dur: int
    cpu: int
    utid: int
    priority: int
    end_state: str = None

    process_name: str = None
    thread_name: str = None

    end_ts: int = None

    def compute_end_ts(self):
        self.end_ts = self.ts + self.dur

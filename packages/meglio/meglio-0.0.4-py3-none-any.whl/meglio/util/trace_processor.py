import os
from typing import List

from perfetto.batch_trace_processor import (
    BatchTraceProcessor,
    BatchTraceProcessorConfig,
)
from perfetto.trace_processor import TraceProcessor, TraceProcessorConfig


def open_trace_file(trace: str):
    return TraceProcessor(
        trace=trace,
        config=TraceProcessorConfig(
            bin_path=os.getenv("TRACE_PROCESSOR_BIN_PATH", None),
        ),
    )


def open_trace_files(traces: List[str]):
    return BatchTraceProcessor(
        traces=traces,
        config=BatchTraceProcessorConfig(
            tp_config=TraceProcessorConfig(
                bin_path=os.getenv("TRACE_PROCESSOR_BIN_PATH", None)
            ),
        ),
    )

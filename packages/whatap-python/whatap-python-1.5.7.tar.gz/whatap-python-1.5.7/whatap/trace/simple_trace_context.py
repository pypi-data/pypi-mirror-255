from whatap.trace.trace_context import TraceContext


class SimpleTraceContext(TraceContext):
    def __init__(self, id, start_time, elapsed, thread_id):
        self.id = id
        self.start_time = start_time
        self.elapsed = elapsed
        self.thread_id = thread_id
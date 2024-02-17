import logging 
from typing import Optional

def get_handler(logger: logging.Logger, name: str):
    """
    Get a handler by name from the logger.
    """
    for handler in logger.handlers:
        if not hasattr(handler, "name"):
            continue
        if handler.name == name:
            return handler
    return None

class MemoryHandler(logging.StreamHandler):
    """
    A handler class which buffers logging records in memory, periodically
    flushing them to a target handler. Flushing occurs whenever the buffer
    is full, or when an event of a certain severity or greater is seen.

    Almost a copy of the standard library MemoryHandler, except that it
    has a formatter.
    """
    def __init__(self, name: str,
                 capacity: int, 
                 flushLevel: int = logging.CRITICAL, 
                 target: callable = None,
                 format: Optional[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                 flushOnClose: Optional[bool] = True):
        """
        Initialize the handler with the buffer size, the level at which
        flushing should occur and an optional target.

        Note that without a target being set either here or via setTarget(),
        a MemoryStreamHandler is no use to anyone!

        The ``flushOnClose`` argument is ``True`` for backward compatibility
        reasons - the old behaviour is that when the handler is closed, the
        buffer is flushed, even if the flush level hasn't been exceeded nor the
        capacity exceeded. To prevent this, set ``flushOnClose`` to ``False``.
        """
        logging.StreamHandler.__init__(self)
        self.name = name
        self.capacity = capacity
        self.buffer = []
        self.flushLevel = flushLevel
        self.target = target
        self.flushOnClose = flushOnClose
        self.setFormatter(logging.Formatter(format))

    def value(self):
        """
        Get the buffered messages as a list of strings.
        """
        return "\n".join(self.buffer)
    
    def emit(self, record):
        """
        Emit a record.

        Append the record. If shouldFlush() tells us to, call flush() to process
        the buffer.
        """
        self.buffer.append(self.format(record))
        if self.shouldFlush(record):
            self.flush()

    def shouldFlush(self, record):
        """
        Check for buffer full or a record at the flushLevel or higher.
        """
        return (len(self.buffer) >= self.capacity) or \
                (record.levelno >= self.flushLevel)

    def setTarget(self, target: callable):
        """
        Set the target handler for this handler.
        """
        self.acquire()
        try:
            self.target = target
        finally:
            self.release()

    def flush(self):
        """
        For a MemoryHandler, flushing means just sending the buffered
        records to the target, if there is one. Override if you want
        different behaviour.

        The record buffer is also cleared by this operation.
        """
        self.acquire()
        try:
            if self.target:
                self.target(self.buffer)
                self.buffer.clear()
        finally:
            self.release()

    def close(self, flush: bool = True):
        """
        Flush, if appropriately configured, set the target to None and lose the
        buffer.
        """
        try:
            if self.flushOnClose and flush:
                self.flush()
            self.buffer.clear()
        finally:
            self.acquire()
            try:
                self.target = None
                logging.Handler.close(self)
            finally:
                self.release()

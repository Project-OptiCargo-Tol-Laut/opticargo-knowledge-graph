import os
import signal
import time


_shutdown = False


def _handle_shutdown(signum, frame):
    global _shutdown
    _ = (signum, frame)
    _shutdown = True


def main() -> None:
    """Minimal infra-compatible graph worker loop."""
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    interval = int(os.getenv("WORKER_HEARTBEAT_SECONDS", "30"))
    print("opticargo-knowledge-graph worker started")
    while not _shutdown:
        print("opticargo-knowledge-graph worker heartbeat")
        time.sleep(interval)
    print("opticargo-knowledge-graph worker stopped")


if __name__ == "__main__":
    main()

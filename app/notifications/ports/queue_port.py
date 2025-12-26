from typing import Protocol, Any


class QueuePort(Protocol):
    """
    Abstract interface for delivering non-email events:
    -async notifications
    -background workers
    -provider webhooks
    -machine health events
    """
    def publish(self, topic: str, payload: Any) -> None:
        """
        Publish a message to a queue or topic.
        """
        ...
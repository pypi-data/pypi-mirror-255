from abc import ABC, abstractmethod


class BaseCaseSummaryBuilder(ABC):
    """Abstract class BaseCaseSummaryBuilder."""

    @abstractmethod
    def run(self, *args, **kwargs):
        """Run the summary builder."""

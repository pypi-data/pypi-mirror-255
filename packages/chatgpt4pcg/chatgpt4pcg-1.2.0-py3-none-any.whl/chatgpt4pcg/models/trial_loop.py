from abc import ABC, abstractmethod

from .trial_context import TrialContext


class TrialLoop(ABC):
    """
    Abstract class for a trial loop.
    """

    @staticmethod
    @abstractmethod
    def run(ctx: TrialContext, target_character: str) -> str:
        pass

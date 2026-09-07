from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract interface for AI providers."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response from the AI provider."""
        raise NotImplementedError
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class Task(ABC, BaseModel):
    """Base class for all tasks that can be assigned to agents.
    
    A task represents a specific operation or job that an agent can perform.
    Tasks should implement the execute() method with their specific logic.
    """
    
    name: str
    description: Optional[str] = None
    config: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the task's main logic.
        
        This method should be implemented by all concrete task classes.
        Returns:
            Any: The result of the task execution
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')" 
from typing import Optional, Any, Dict, List
from threading import Thread
from uuid import uuid4
import time

from loguru import logger


class Agent:
    """Base class for all AgentForge agents.
    
    An agent is a background process that can be assigned tasks and run continuously
    or on-demand. Agents can communicate with each other and react to events.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.id = str(uuid4())
        self.name = name
        self.config = config or {}
        self.tasks: List[Any] = []
        self._thread: Optional[Thread] = None
        self._running = False
        
        logger.info(f"Agent {self.name} ({self.id}) initialized")
    
    def assign_task(self, task: Any) -> None:
        """Assign a task to this agent."""
        self.tasks.append(task)
        logger.info(f"Task {task.__class__.__name__} assigned to agent {self.name}")
    
    def start(self) -> None:
        """Start the agent in a background thread."""
        if self._running:
            logger.warning(f"Agent {self.name} is already running")
            return
            
        self._running = True
        self._thread = Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f"Agent {self.name} started")
    
    def stop(self) -> None:
        """Stop the agent."""
        self._running = False
        if self._thread:
            self._thread.join()
            logger.info(f"Agent {self.name} stopped")
    
    def _run_loop(self) -> None:
        """Main agent loop that processes tasks."""
        while self._running:
            for task in self.tasks:
                try:
                    task.execute()
                except Exception as e:
                    logger.error(f"Error in agent {self.name} executing task: {e}")
            time.sleep(1)  # Basic rate limiting
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', id='{self.id}', tasks={len(self.tasks)})" 

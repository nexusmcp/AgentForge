import pytest
from decimal import Decimal

from agentforge.core import Agent
from agentforge.tasks.base import Task
from agentforge.tasks.price_tracking import PriceTrackingTask


def test_agent_initialization():
    """Test that an agent can be properly initialized."""
    agent = Agent("test_agent")
    assert agent.name == "test_agent"
    assert len(agent.tasks) == 0


def test_agent_task_assignment():
    """Test that tasks can be assigned to an agent."""
    agent = Agent("test_agent")
    task = PriceTrackingTask(
        token_address="0x123",
        threshold_price=Decimal("100.00")
    )
    
    agent.assign_task(task)
    assert len(agent.tasks) == 1
    assert isinstance(agent.tasks[0], Task)


def test_agent_start_stop():
    """Test that an agent can be started and stopped."""
    agent = Agent("test_agent")
    task = PriceTrackingTask(
        token_address="0x123",
        threshold_price=Decimal("100.00")
    )
    
    agent.assign_task(task)
    agent.start()
    assert agent._running is True
    
    agent.stop()
    assert agent._running is False 

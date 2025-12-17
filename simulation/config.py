"""Default configuration values for the simulation."""
from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Configuration for stock and flow simulation parameters."""
    
    # Initial state
    initial_open_tickets: int = 100
    initial_started_coding: int = 0
    initial_tested_code: int = 0
    initial_deployed_code: int = 0
    initial_closed_tickets: int = 0
    
    # Flow rates (tickets per time step)
    ticket_open_rate: int = 10
    start_coding_rate: int = 10
    testing_rate: int = 10
    deployment_rate: int = 10
    close_rate: int = 10
    
    # Capacity constraints
    max_concurrent_coding: int = 50
    
    # Error rates (as percentages, 0.0 to 1.0)
    testing_error_rate: float = 0.15
    deployment_error_rate: float = 0.10
    production_error_rate: float = 0.25
    
    # Simulation settings
    duration: int = 100  # number of time steps
    
    def __post_init__(self):
        """Validate configuration values."""
        assert 0.0 <= self.testing_error_rate <= 1.0
        assert 0.0 <= self.deployment_error_rate <= 1.0
        assert 0.0 <= self.production_error_rate <= 1.0
        assert self.duration > 0

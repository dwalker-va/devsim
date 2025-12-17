"""Core stock and flow simulation engine."""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from .config import SimulationConfig


class StockFlowSimulation:
    """
    Simulates a software development stock and flow model.
    
    Based on Will Larson's model with five stocks:
    - Open Tickets
    - Started Coding
    - Tested Code
    - Deployed Code
    - Closed Tickets
    
    Includes forward flows (left-to-right) and backward error flows.
    """
    
    def __init__(self, config: SimulationConfig):
        """
        Initialize the simulation with given configuration.
        
        Args:
            config: SimulationConfig object with all parameters
        """
        self.config = config
        self.reset()
    
    def reset(self):
        """Reset simulation to initial state."""
        # Initialize stocks
        self.stocks = {
            'open_tickets': self.config.initial_open_tickets,
            'started_coding': self.config.initial_started_coding,
            'tested_code': self.config.initial_tested_code,
            'deployed_code': self.config.initial_deployed_code,
            'closed_tickets': self.config.initial_closed_tickets,
        }
        
        # Initialize history tracking
        self.history = {
            'time_step': [0],
            'open_tickets': [self.stocks['open_tickets']],
            'started_coding': [self.stocks['started_coding']],
            'tested_code': [self.stocks['tested_code']],
            'deployed_code': [self.stocks['deployed_code']],
            'closed_tickets': [self.stocks['closed_tickets']],
        }
        
        # Flow history for visualization
        self.flow_history = {
            'time_step': [0],
            'start_coding_flow': [0],
            'testing_flow': [0],
            'deployment_flow': [0],
            'closing_flow': [0],
            'testing_error_flow': [0],
            'deployment_error_flow': [0],
            'production_error_flow': [0],
        }
        
        self.current_step = 0
    
    def step(self) -> Dict[str, float]:
        """
        Execute one time step of the simulation.
        
        Returns:
            Dict with current stock values after the step
        """
        # Store current stocks for flow calculations
        current = self.stocks.copy()
        
        # Calculate forward flows (left to right)
        
        # Flow 1: Open Tickets -> Started Coding
        # Limited by: start_coding_rate AND max_concurrent_coding capacity
        available_capacity = max(0, self.config.max_concurrent_coding - current['started_coding'])
        start_coding_flow = min(
            self.config.start_coding_rate,
            current['open_tickets'],
            available_capacity
        )
        
        # Flow 2: Started Coding -> Tested Code
        # Limited by: testing_rate AND available items
        testing_flow = min(
            self.config.testing_rate,
            current['started_coding']
        )
        
        # Flow 3: Tested Code -> Deployed Code
        # Limited by: deployment_rate AND available items
        deployment_flow = min(
            self.config.deployment_rate,
            current['tested_code']
        )
        
        # Flow 4: Deployed Code -> Closed Tickets
        # Limited by: close_rate AND available items
        closing_flow = min(
            self.config.close_rate,
            current['deployed_code']
        )
        
        # Calculate backward error flows (right to left)
        
        # Error flow 1: Tested Code -> Started Coding (testing found errors)
        testing_error_flow = int(np.floor(current['tested_code'] * self.config.testing_error_rate))
        
        # Error flow 2: Deployed Code -> Started Coding (deployment exposed errors)
        deployment_error_flow = int(np.floor(current['deployed_code'] * self.config.deployment_error_rate))
        
        # Error flow 3: Closed Tickets -> Open Tickets (production errors)
        production_error_flow = int(np.floor(current['closed_tickets'] * self.config.production_error_rate))
        
        # Update stocks based on all flows
        
        # Open Tickets: +ticket_open_rate, +production_error_flow, -start_coding_flow
        self.stocks['open_tickets'] = max(0, 
            current['open_tickets'] 
            + self.config.ticket_open_rate 
            + production_error_flow 
            - start_coding_flow
        )
        
        # Started Coding: +start_coding_flow, +testing_error_flow, +deployment_error_flow, -testing_flow
        self.stocks['started_coding'] = max(0,
            current['started_coding']
            + start_coding_flow
            + testing_error_flow
            + deployment_error_flow
            - testing_flow
        )
        
        # Tested Code: +testing_flow, -testing_error_flow, -deployment_flow
        self.stocks['tested_code'] = max(0,
            current['tested_code']
            + testing_flow
            - testing_error_flow
            - deployment_flow
        )
        
        # Deployed Code: +deployment_flow, -deployment_error_flow, -closing_flow
        self.stocks['deployed_code'] = max(0,
            current['deployed_code']
            + deployment_flow
            - deployment_error_flow
            - closing_flow
        )
        
        # Closed Tickets: +closing_flow, -production_error_flow
        self.stocks['closed_tickets'] = max(0,
            current['closed_tickets']
            + closing_flow
            - production_error_flow
        )
        
        # Increment step counter
        self.current_step += 1
        
        # Record history
        self.history['time_step'].append(self.current_step)
        for stock_name, value in self.stocks.items():
            self.history[stock_name].append(value)
        
        # Record flow history
        self.flow_history['time_step'].append(self.current_step)
        self.flow_history['start_coding_flow'].append(start_coding_flow)
        self.flow_history['testing_flow'].append(testing_flow)
        self.flow_history['deployment_flow'].append(deployment_flow)
        self.flow_history['closing_flow'].append(closing_flow)
        self.flow_history['testing_error_flow'].append(testing_error_flow)
        self.flow_history['deployment_error_flow'].append(deployment_error_flow)
        self.flow_history['production_error_flow'].append(production_error_flow)
        
        return self.stocks.copy()
    
    def run(self, steps: int = None) -> pd.DataFrame:
        """
        Run the simulation for a given number of steps.
        
        Args:
            steps: Number of steps to run (defaults to config.duration)
            
        Returns:
            DataFrame with history of all stock values
        """
        if steps is None:
            steps = self.config.duration
        
        for _ in range(steps):
            self.step()
        
        return self.get_history_df()
    
    def get_history_df(self) -> pd.DataFrame:
        """
        Get simulation history as a pandas DataFrame.
        
        Returns:
            DataFrame with columns for time_step and each stock
        """
        return pd.DataFrame(self.history)
    
    def get_flow_history_df(self) -> pd.DataFrame:
        """
        Get flow history as a pandas DataFrame.
        
        Returns:
            DataFrame with columns for time_step and each flow
        """
        return pd.DataFrame(self.flow_history)
    
    def get_current_flows(self) -> Dict[str, float]:
        """
        Get the most recent flow values.
        
        Returns:
            Dict with flow names and their current values
        """
        if len(self.flow_history['time_step']) <= 1:
            return {key: 0 for key in self.flow_history.keys() if key != 'time_step'}
        
        return {
            key: values[-1] 
            for key, values in self.flow_history.items() 
            if key != 'time_step'
        }

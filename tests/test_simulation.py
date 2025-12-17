"""Tests for the stock and flow simulation engine."""
import pytest
from simulation import StockFlowSimulation, SimulationConfig


class TestSimulationConfig:
    """Tests for SimulationConfig."""
    
    def test_default_config(self):
        """Test that default configuration is valid."""
        config = SimulationConfig()
        assert config.initial_open_tickets >= 0
        assert 0.0 <= config.testing_error_rate <= 1.0
        assert 0.0 <= config.deployment_error_rate <= 1.0
        assert 0.0 <= config.production_error_rate <= 1.0
        assert config.duration > 0
    
    def test_invalid_error_rate_raises(self):
        """Test that invalid error rates raise an assertion error."""
        with pytest.raises(AssertionError):
            SimulationConfig(testing_error_rate=1.5)
        
        with pytest.raises(AssertionError):
            SimulationConfig(production_error_rate=-0.1)


class TestStockFlowSimulation:
    """Tests for StockFlowSimulation."""
    
    def test_initialization(self):
        """Test that simulation initializes correctly."""
        config = SimulationConfig(initial_open_tickets=50)
        sim = StockFlowSimulation(config)
        
        assert sim.stocks['open_tickets'] == 50
        assert sim.stocks['started_coding'] == 0
        assert sim.current_step == 0
        assert len(sim.history['time_step']) == 1
    
    def test_reset(self):
        """Test that reset returns simulation to initial state."""
        config = SimulationConfig(initial_open_tickets=100)
        sim = StockFlowSimulation(config)
        
        # Run a few steps
        sim.step()
        sim.step()
        assert sim.current_step == 2
        
        # Reset
        sim.reset()
        assert sim.current_step == 0
        assert sim.stocks['open_tickets'] == 100
        assert len(sim.history['time_step']) == 1
    
    def test_step_increments_time(self):
        """Test that step increments the time counter."""
        config = SimulationConfig()
        sim = StockFlowSimulation(config)
        
        initial_step = sim.current_step
        sim.step()
        assert sim.current_step == initial_step + 1
    
    def test_tickets_flow_forward(self):
        """Test that tickets flow through the system."""
        config = SimulationConfig(
            initial_open_tickets=100,
            ticket_open_rate=0,  # Don't add new tickets
            start_coding_rate=10,
            testing_rate=10,
            deployment_rate=10,
            close_rate=10,
            max_concurrent_coding=100,
            testing_error_rate=0.0,
            deployment_error_rate=0.0,
            production_error_rate=0.0,
        )
        sim = StockFlowSimulation(config)
        
        # Initial state
        assert sim.stocks['open_tickets'] == 100
        assert sim.stocks['closed_tickets'] == 0
        
        # After one step, some tickets should start coding
        sim.step()
        assert sim.stocks['open_tickets'] == 90  # 10 moved to coding
        assert sim.stocks['started_coding'] == 10
        
        # After another step, those tickets should move to testing
        sim.step()
        assert sim.stocks['started_coding'] == 10  # 10 new in, 10 out
        assert sim.stocks['tested_code'] == 10
        
        # Continue through the pipeline
        sim.step()  # Move to deployed
        assert sim.stocks['deployed_code'] == 10
        
        sim.step()  # Close tickets
        assert sim.stocks['closed_tickets'] == 10
    
    def test_capacity_constraint(self):
        """Test that max concurrent coding is respected."""
        config = SimulationConfig(
            initial_open_tickets=100,
            start_coding_rate=50,
            max_concurrent_coding=20,  # Constraint
            testing_rate=0,  # Don't move anything out
        )
        sim = StockFlowSimulation(config)
        
        # First step should respect capacity
        sim.step()
        assert sim.stocks['started_coding'] <= 20
        
        # Second step shouldn't add more beyond capacity
        sim.step()
        assert sim.stocks['started_coding'] <= 20
    
    def test_error_flows_backward(self):
        """Test that errors cause tickets to flow backward."""
        config = SimulationConfig(
            initial_open_tickets=0,
            initial_closed_tickets=100,
            ticket_open_rate=0,
            production_error_rate=0.1,  # 10% error rate
        )
        sim = StockFlowSimulation(config)
        
        initial_closed = sim.stocks['closed_tickets']
        
        # After one step, some closed tickets should reopen
        sim.step()
        errors = int(initial_closed * 0.1)
        
        assert sim.stocks['closed_tickets'] < initial_closed
        assert sim.stocks['open_tickets'] >= errors
    
    def test_run_completes(self):
        """Test that run method completes successfully."""
        config = SimulationConfig(duration=50)
        sim = StockFlowSimulation(config)
        
        df = sim.run()
        
        assert len(df) == 51  # 0 to 50 inclusive
        assert df['time_step'].max() == 50
        assert 'open_tickets' in df.columns
        assert 'closed_tickets' in df.columns
    
    def test_history_tracking(self):
        """Test that history is tracked correctly."""
        config = SimulationConfig(duration=10)
        sim = StockFlowSimulation(config)
        
        sim.run()
        
        history_df = sim.get_history_df()
        flow_df = sim.get_flow_history_df()
        
        assert len(history_df) == 11  # 0 to 10
        assert len(flow_df) == 11
        assert 'time_step' in history_df.columns
        assert 'start_coding_flow' in flow_df.columns
    
    def test_no_negative_stocks(self):
        """Test that stocks never go negative."""
        config = SimulationConfig(
            initial_open_tickets=10,
            ticket_open_rate=0,
            start_coding_rate=100,  # Try to take more than available
        )
        sim = StockFlowSimulation(config)
        
        sim.run(steps=20)
        
        history_df = sim.get_history_df()
        
        # Check all stocks remain non-negative
        for col in ['open_tickets', 'started_coding', 'tested_code', 'deployed_code', 'closed_tickets']:
            assert (history_df[col] >= 0).all(), f"{col} went negative"
    
    def test_equilibrium_with_high_error_rate(self):
        """Test that high error rates prevent progress."""
        config = SimulationConfig(
            initial_open_tickets=100,
            production_error_rate=0.5,  # Very high error rate
            duration=100,
        )
        sim = StockFlowSimulation(config)
        
        sim.run()
        history_df = sim.get_history_df()
        
        # With high error rate, closed tickets should plateau
        final_closed = history_df['closed_tickets'].iloc[-1]
        mid_closed = history_df['closed_tickets'].iloc[len(history_df)//2]
        
        # Progress should slow significantly in second half
        first_half_growth = mid_closed - history_df['closed_tickets'].iloc[0]
        second_half_growth = final_closed - mid_closed
        
        # Second half growth should be less than first half
        # (this demonstrates the equilibrium effect)
        assert second_half_growth <= first_half_growth


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

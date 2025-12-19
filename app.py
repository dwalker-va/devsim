"""
Stock & Flow Simulation - Developer Velocity Model

Interactive simulation based on Will Larson's blog post:
https://lethain.com/dx-llm-model/

This application simulates the software development process as a stock and flow system
to understand how different factors (error rates, flow rates, capacity) impact velocity.
"""

import streamlit as st
import plotly.graph_objects as go
from simulation import StockFlowSimulation, SimulationConfig
from visualization import AnimatedDiagram

# Page configuration
st.set_page_config(
    page_title="Stock & Flow Simulation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📊 Developer Velocity Stock & Flow Simulation")
st.markdown("""
This simulation models the software development process to understand how different factors impact velocity.
Based on [Will Larson's systems model](https://lethain.com/dx-llm-model/).

Experiment with different parameters to discover which factors have the biggest impact on your delivery velocity.
""")

# Initialize session state for simulation persistence
if 'simulation' not in st.session_state:
    st.session_state.simulation = None
if 'history_df' not in st.session_state:
    st.session_state.history_df = None
if 'flow_history_df' not in st.session_state:
    st.session_state.flow_history_df = None

# Sidebar - Parameter Controls
st.sidebar.header("⚙️ Simulation Parameters")

# Error Rates Section
st.sidebar.subheader("🔴 Error Rates")
st.sidebar.markdown("*Percentage of items that encounter errors*")

testing_error_rate = st.sidebar.slider(
    "Bugs Found in Testing",
    min_value=0.0,
    max_value=0.5,
    value=0.15,
    step=0.01,
    format="%.2f",
    help="Fraction of items in testing that have bugs discovered"
)

deployment_error_rate = st.sidebar.slider(
    "Release Blocked Rate",
    min_value=0.0,
    max_value=0.5,
    value=0.10,
    step=0.01,
    format="%.2f",
    help="Fraction of releases that encounter blocking issues"
)

production_error_rate = st.sidebar.slider(
    "Production Defect Rate",
    min_value=0.0,
    max_value=0.5,
    value=0.25,
    step=0.01,
    format="%.2f",
    help="Fraction of live items that have defects discovered in production"
)

st.sidebar.divider()

# Flow Rates Section
st.sidebar.subheader("⚡ Flow Rates")
st.sidebar.markdown("*Items processed per time step*")

ticket_open_rate = st.sidebar.slider(
    "New Work Added to Backlog",
    min_value=1,
    max_value=100,
    value=10,
    help="Number of new items added to backlog per time step"
)

start_coding_rate = st.sidebar.slider(
    "Start Development Rate",
    min_value=1,
    max_value=100,
    value=10,
    help="Number of items that can begin development per time step"
)

testing_rate = st.sidebar.slider(
    "Testing Throughput",
    min_value=1,
    max_value=100,
    value=10,
    help="Number of items that can be tested per time step"
)

deployment_rate = st.sidebar.slider(
    "Release Staging Rate",
    min_value=1,
    max_value=100,
    value=10,
    help="Number of items that can be staged for release per time step"
)

close_rate = st.sidebar.slider(
    "Go Live Rate",
    min_value=1,
    max_value=100,
    value=10,
    help="Number of items that can go live per time step"
)

st.sidebar.divider()

# Capacity Constraints Section
st.sidebar.subheader("🎯 Capacity Constraints")

max_concurrent_coding = st.sidebar.slider(
    "Max Work in Progress",
    min_value=1,
    max_value=200,
    value=50,
    help="Maximum number of items that can be in development simultaneously (WIP limit)"
)

st.sidebar.divider()

# Initial State Section
st.sidebar.subheader("🎬 Initial State")

initial_open_tickets = st.sidebar.number_input(
    "Initial Backlog Size",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    help="Number of items in backlog at the start of simulation"
)

st.sidebar.divider()

# Simulation Settings Section
st.sidebar.subheader("⏱️ Simulation Settings")

duration = st.sidebar.slider(
    "Simulation Duration (time steps)",
    min_value=20,
    max_value=200,
    value=100,
    help="Number of time steps to simulate"
)

# Run Simulation Button
st.sidebar.divider()
run_button = st.sidebar.button("▶️ Run Simulation", type="primary", use_container_width=True)

if run_button or st.session_state.simulation is None:
    # Create configuration
    config = SimulationConfig(
        initial_open_tickets=initial_open_tickets,
        initial_started_coding=0,
        initial_tested_code=0,
        initial_deployed_code=0,
        initial_closed_tickets=0,
        ticket_open_rate=ticket_open_rate,
        start_coding_rate=start_coding_rate,
        testing_rate=testing_rate,
        deployment_rate=deployment_rate,
        close_rate=close_rate,
        max_concurrent_coding=max_concurrent_coding,
        testing_error_rate=testing_error_rate,
        deployment_error_rate=deployment_error_rate,
        production_error_rate=production_error_rate,
        duration=duration,
    )
    
    # Run simulation
    with st.spinner("Running simulation..."):
        simulation = StockFlowSimulation(config)
        simulation.run()
        
        # Store in session state
        st.session_state.simulation = simulation
        st.session_state.history_df = simulation.get_history_df()
        st.session_state.flow_history_df = simulation.get_flow_history_df()
    
    st.sidebar.success("✅ Simulation complete!")

# Reset Button
if st.sidebar.button("🔄 Reset to Defaults", use_container_width=True):
    st.session_state.simulation = None
    st.session_state.history_df = None
    st.session_state.flow_history_df = None
    st.rerun()

# Main content area
if st.session_state.simulation is not None:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Stock Levels Over Time", "🔀 Stock & Flow Diagram", "📈 Flow Rates"])
    
    with tab1:
        st.subheader("Stock Levels Over Time")
        
        # Create line chart of stock levels
        history_df = st.session_state.history_df
        
        fig_stocks = go.Figure()
        
        colors = {
            'open_tickets': '#e74c3c',
            'started_coding': '#f39c12',
            'tested_code': '#3498db',
            'deployed_code': '#9b59b6',
            'closed_tickets': '#2ecc71',
        }
        
        stock_names = {
            'open_tickets': 'Backlog',
            'started_coding': 'In Development',
            'tested_code': 'In Testing',
            'deployed_code': 'Awaiting Release',
            'closed_tickets': 'Live in Production',
        }
        
        for stock_col, display_name in stock_names.items():
            fig_stocks.add_trace(go.Scatter(
                x=history_df['time_step'],
                y=history_df[stock_col],
                mode='lines',
                name=display_name,
                line=dict(color=colors[stock_col], width=3),
                hovertemplate=f'<b>{display_name}</b><br>Time: %{{x}}<br>Count: %{{y}}<extra></extra>'
            ))
        
        fig_stocks.update_layout(
            xaxis_title="Time Step",
            yaxis_title="Number of Items",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
        )
        
        st.plotly_chart(fig_stocks, use_container_width=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        final_closed = history_df['closed_tickets'].iloc[-1]
        final_open = history_df['open_tickets'].iloc[-1]
        max_in_progress = history_df['started_coding'].max()
        
        with col1:
            st.metric("Items Live in Production", f"{int(final_closed)}")
        
        with col2:
            st.metric("Items in Backlog", f"{int(final_open)}")
        
        with col3:
            st.metric("Peak Work in Progress", f"{int(max_in_progress)}")
        
        with col4:
            avg_velocity = final_closed / duration if duration > 0 else 0
            st.metric("Avg Velocity", f"{avg_velocity:.1f} items/step")
    
    with tab2:
        st.subheader("Stock & Flow Diagram")
        st.markdown("*Visual representation of the development process stages*")
        
        # Create the diagram
        diagram = AnimatedDiagram()
        
        # Get current state (last time step)
        current_stocks = {
            'open_tickets': history_df['open_tickets'].iloc[-1],
            'started_coding': history_df['started_coding'].iloc[-1],
            'tested_code': history_df['tested_code'].iloc[-1],
            'deployed_code': history_df['deployed_code'].iloc[-1],
            'closed_tickets': history_df['closed_tickets'].iloc[-1],
        }
        
        flow_history_df = st.session_state.flow_history_df
        current_flows = {
            'start_coding_flow': flow_history_df['start_coding_flow'].iloc[-1],
            'testing_flow': flow_history_df['testing_flow'].iloc[-1],
            'deployment_flow': flow_history_df['deployment_flow'].iloc[-1],
            'closing_flow': flow_history_df['closing_flow'].iloc[-1],
            'testing_error_flow': flow_history_df['testing_error_flow'].iloc[-1],
            'deployment_error_flow': flow_history_df['deployment_error_flow'].iloc[-1],
            'production_error_flow': flow_history_df['production_error_flow'].iloc[-1],
        }
        
        fig_diagram = diagram.create_static_diagram(current_stocks, current_flows)
        st.plotly_chart(fig_diagram, use_container_width=True)
        
        st.markdown("""
        **Legend:**
        - 🟢 **Green arrows**: Forward flows (left to right)
        - 🔴 **Red dashed arrows**: Error flows (right to left)
        - Numbers in boxes show current ticket counts in each stage
        """)
    
    with tab3:
        st.subheader("Flow Rates Over Time")
        
        flow_history_df = st.session_state.flow_history_df
        
        # Forward flows
        st.markdown("**Forward Flows**")
        fig_forward = go.Figure()
        
        forward_flows = {
            'start_coding_flow': 'Start Development',
            'testing_flow': 'Begin Testing',
            'deployment_flow': 'Stage for Release',
            'closing_flow': 'Go Live',
        }
        
        for flow_col, display_name in forward_flows.items():
            fig_forward.add_trace(go.Scatter(
                x=flow_history_df['time_step'],
                y=flow_history_df[flow_col],
                mode='lines',
                name=display_name,
                line=dict(width=2),
            ))
        
        fig_forward.update_layout(
            xaxis_title="Time Step",
            yaxis_title="Items Processed",
            hovermode='x unified',
            height=300,
        )
        
        st.plotly_chart(fig_forward, use_container_width=True)
        
        # Error flows
        st.markdown("**Error Flows (Rework)**")
        fig_errors = go.Figure()
        
        error_flows = {
            'testing_error_flow': 'Bugs Found in Testing',
            'deployment_error_flow': 'Release Blocked',
            'production_error_flow': 'Defects in Production',
        }
        
        colors_errors = ['#e74c3c', '#e67e22', '#c0392b']
        
        for i, (flow_col, display_name) in enumerate(error_flows.items()):
            fig_errors.add_trace(go.Scatter(
                x=flow_history_df['time_step'],
                y=flow_history_df[flow_col],
                mode='lines',
                name=display_name,
                line=dict(width=2, color=colors_errors[i]),
            ))
        
        fig_errors.update_layout(
            xaxis_title="Time Step",
            yaxis_title="Items Requiring Rework",
            hovermode='x unified',
            height=300,
        )
        
        st.plotly_chart(fig_errors, use_container_width=True)
        
        # Total rework metric
        total_rework = (
            flow_history_df['testing_error_flow'].sum() +
            flow_history_df['deployment_error_flow'].sum() +
            flow_history_df['production_error_flow'].sum()
        )
        
        st.metric("Total Rework (all error flows)", f"{int(total_rework)} items")

else:
    # Initial state - show instructions
    st.info("👈 Configure simulation parameters in the sidebar and click **Run Simulation** to begin.")
    
    st.markdown("""
    ### About This Model
    
    This simulation implements a stock and flow model of the software development process with five stages:
    
    1. **Backlog** - Work waiting to be started
    2. **In Development** - Work in active development
    3. **In Testing** - Work that has been tested
    4. **Awaiting Release** - Work staged for production
    5. **Live in Production** - Completed work deployed to users
    
    The model includes three types of error flows that move work backwards:
    
    - **Bugs Found in Testing**: Issues discovered during testing send work back to development
    - **Release Blocked**: Problems during release staging send work back to development
    - **Defects in Production**: Bugs found in production return work to the backlog
    
    ### How to Use
    
    1. Adjust the parameters in the sidebar to match your organization
    2. Click "Run Simulation" to see the results
    3. Experiment with different values to understand their impact
    4. Compare scenarios by adjusting one parameter at a time
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 0.9em;'>
    Based on <a href='https://lethain.com/dx-llm-model/' target='_blank'>Will Larson's Developer Experience Model</a>
</div>
""", unsafe_allow_html=True)

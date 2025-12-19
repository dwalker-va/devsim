# Stock & Flow Simulation - Developer Velocity Model

An interactive simulation of the software development process as a stock and flow system, based on [Will Larson's Developer Experience Model](https://lethain.com/dx-llm-model/).

## Overview

This application helps visualize and understand how different factors in the development process impact overall velocity:

- **Error rates** at different stages (testing, deployment, production)
- **Flow rates** for each development stage
- **Capacity constraints** on work in progress
- **Initial conditions** and simulation duration

### Key Insight

The model demonstrates that **production error rate is often the primary constraint** on velocity, not development speed. Increasing development velocity while maintaining high error rates can actually be counterproductive.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## How to Use

1. **Configure Parameters**: Use the sidebar to adjust simulation parameters:
   - **Error Rates**: Set the percentage of work that encounters errors at each stage
   - **Flow Rates**: Set how many tickets can be processed per time step at each stage
   - **Capacity Constraints**: Set the maximum concurrent work in progress
   - **Initial State**: Set the starting number of open tickets
   - **Simulation Duration**: Set how many time steps to simulate

2. **Run Simulation**: Click the "Run Simulation" button to execute the model

3. **Analyze Results**: Explore three views:
   - **Stock Levels Over Time**: Line chart showing ticket counts in each stage
   - **Stock & Flow Diagram**: Visual representation of the development pipeline
   - **Flow Rates**: Charts showing forward flows and error flows over time

4. **Experiment**: Try different scenarios to understand their impact:
   - Reduce production error rate (often has the biggest impact)
   - Increase development speed (may not help if error rates are high)
   - Adjust capacity constraints to see bottleneck effects

## The Model

### Five Stocks (Stages)

1. **Backlog** - Work waiting to be started
2. **In Development** - Work in active development
3. **In Testing** - Work that has been tested
4. **Awaiting Release** - Work staged for production
5. **Live in Production** - Completed work deployed to users

### Forward Flows (Left to Right)

- Ticket Opening → Start Coding → Testing → Deployment → Closing

### Backward Error Flows (Right to Left)

- **Bugs Found in Testing**: In Testing → In Development
- **Release Blocked**: Awaiting Release → In Development
- **Defects in Production**: Live in Production → Backlog

### Key Dynamics

- Tickets flow left-to-right through the development process
- Errors cause tickets to flow backward (rework)
- Each stage has a maximum flow rate
- Capacity constraints limit work in progress
- The system reaches equilibrium when error generation balances completion rate

## Parameter Ranges

Default ranges are scaled for a typical development organization:

- **Error Rates**: 0% to 50% (0.0 to 0.5)
- **Flow Rates**: 1 to 100 tickets per time step
- **Max Concurrent**: 1 to 200 tickets
- **Initial Backlog Size**: 10 to 1000
- **Simulation Duration**: 20 to 200 time steps

Adjust these ranges in the code if your organization operates at a different scale.

## Example Scenarios

### Scenario 1: High Production Error Rate (Baseline)

```
Production Error Rate: 25%
Other Errors: 10-15%
Flow Rates: All at 10
```

**Result**: System reaches equilibrium quickly. Items live in production plateau as production defects keep returning work to the backlog.

### Scenario 2: Improved Testing (Lower Production Errors)

```
Production Error Rate: 10% (reduced!)
Testing Error Rate: 20% (increased)
Other parameters: Same as baseline
```

**Result**: More time spent in testing loop (catching errors early), but many more items successfully go live over time.

### Scenario 3: Faster Development, Same Errors

```
All Flow Rates: 30 (3x faster)
Error Rates: Same as baseline
```

**Result**: Minimal improvement in items going live. The constraint is error rate, not development speed.

## Project Structure

```
devsim/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── simulation/
│   ├── __init__.py
│   ├── engine.py          # Core simulation logic
│   └── config.py          # Configuration dataclass
├── visualization/
│   ├── __init__.py
│   └── diagram.py         # Plotly diagram renderer
└── tests/
    ├── __init__.py
    └── test_simulation.py # Unit tests
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Or with verbose output:

```bash
pytest tests/ -v
```

## Customization

### Modifying Parameter Ranges

Edit the slider parameters in `app.py` to adjust ranges for your organization's scale.

### Adding New Metrics

The simulation tracks stock levels and flows. You can add custom metrics by:

1. Calculating them from the history DataFrames
2. Adding new visualizations in `app.py`

### Extending the Model

The model can be extended to include:

- Multiple development teams
- Different ticket priorities
- Seasonal variations in ticket opening rates
- More granular error types
- Resource constraints (engineers, infrastructure)

Edit `simulation/engine.py` to modify the core model logic.

## Deployment

### Streamlit Cloud (Recommended)

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy the app

The app will be publicly accessible via a streamlit.io URL.

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t devsim .
docker run -p 8501:8501 devsim
```

## References

- [Will Larson's Blog Post](https://lethain.com/dx-llm-model/) - Original systems model
- [System Dynamics](https://en.wikipedia.org/wiki/System_dynamics) - Methodology background
- [Streamlit Documentation](https://docs.streamlit.io/) - UI framework
- [Plotly Documentation](https://plotly.com/python/) - Visualization library

## License

See LICENSE file for details.

## Contributing

This is a demonstration project. Feel free to fork and modify for your organization's needs.

## Contact

Created as a learning tool to understand developer velocity dynamics through systems thinking.

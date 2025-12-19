"""Animated stock and flow diagram visualization."""
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Tuple
import pandas as pd


class AnimatedDiagram:
    """
    Creates an animated Plotly diagram showing stocks and flows.
    
    Visualizes the five-stage development process with:
    - Stock boxes showing current values
    - Animated particles flowing between stages
    - Color-coded error flows going backward
    """
    
    # Stock positions (x, y coordinates)
    STOCK_POSITIONS = {
        'open_tickets': (0, 2),
        'started_coding': (2, 2),
        'tested_code': (4, 2),
        'deployed_code': (6, 2),
        'closed_tickets': (8, 2),
    }
    
    # Stock display names
    STOCK_NAMES = {
        'open_tickets': 'Backlog',
        'started_coding': 'In Development',
        'tested_code': 'In Testing',
        'deployed_code': 'Awaiting Release',
        'closed_tickets': 'Live in Production',
    }
    
    # Colors
    COLOR_STOCK = '#3498db'
    COLOR_FORWARD_FLOW = '#2ecc71'
    COLOR_ERROR_FLOW = '#e74c3c'
    COLOR_TEXT = '#2c3e50'
    
    def __init__(self):
        """Initialize the animated diagram."""
        pass
    
    def create_static_diagram(
        self, 
        stocks: Dict[str, float],
        flows: Dict[str, float] = None
    ) -> go.Figure:
        """
        Create a static (non-animated) diagram showing current state.
        
        Args:
            stocks: Dict with stock names and current values
            flows: Dict with flow names and current values (optional)
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Add stock boxes
        for stock_name, (x, y) in self.STOCK_POSITIONS.items():
            value = stocks.get(stock_name, 0)
            display_name = self.STOCK_NAMES[stock_name]
            
            # Add box
            fig.add_shape(
                type="rect",
                x0=x-0.4, y0=y-0.3,
                x1=x+0.4, y1=y+0.3,
                line=dict(color=self.COLOR_STOCK, width=3),
                fillcolor='rgba(52, 152, 219, 0.1)',
            )
            
            # Add label
            fig.add_annotation(
                x=x, y=y+0.15,
                text=f"<b>{display_name}</b>",
                showarrow=False,
                font=dict(size=11, color=self.COLOR_TEXT),
            )
            
            # Add value
            fig.add_annotation(
                x=x, y=y-0.1,
                text=f"{int(value)}",
                showarrow=False,
                font=dict(size=16, color=self.COLOR_TEXT, family="monospace"),
            )
        
        # Add forward flow arrows
        self._add_arrow(fig, 0.4, 2, 1.6, 2, self.COLOR_FORWARD_FLOW, "→ Start Work")
        self._add_arrow(fig, 2.4, 2, 3.6, 2, self.COLOR_FORWARD_FLOW, "→ Begin Testing")
        self._add_arrow(fig, 4.4, 2, 5.6, 2, self.COLOR_FORWARD_FLOW, "→ Stage Release")
        self._add_arrow(fig, 6.4, 2, 7.6, 2, self.COLOR_FORWARD_FLOW, "→ Go Live")
        
        # Add error flow arrows (curved, going backward)
        # Testing error: In Testing -> In Development
        self._add_curved_arrow(fig, 3.8, 2.35, 2.2, 2.35, self.COLOR_ERROR_FLOW, "Bugs Found", offset=0.6)
        
        # Deployment error: Awaiting Release -> In Development
        self._add_curved_arrow(fig, 5.8, 2.35, 2.2, 2.35, self.COLOR_ERROR_FLOW, "Release Blocked", offset=0.9)
        
        # Production error: Live in Production -> Backlog
        self._add_curved_arrow(fig, 7.8, 2.35, 0.2, 2.35, self.COLOR_ERROR_FLOW, "Prod Defects", offset=1.2)
        
        # Add flow values if provided
        if flows:
            self._add_flow_annotations(fig, flows)
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            width=1200,
            height=500,
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[-0.5, 8.5],
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[0, 4],
                scaleanchor="x",
                scaleratio=1,
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        return fig
    
    def create_animated_diagram(
        self,
        history_df: pd.DataFrame,
        flow_history_df: pd.DataFrame
    ) -> go.Figure:
        """
        Create an animated diagram showing the simulation over time.
        
        Args:
            history_df: DataFrame with stock history
            flow_history_df: DataFrame with flow history
            
        Returns:
            Plotly Figure with animation frames
        """
        # Start with the initial frame
        initial_stocks = {
            'open_tickets': history_df['open_tickets'].iloc[0],
            'started_coding': history_df['started_coding'].iloc[0],
            'tested_code': history_df['tested_code'].iloc[0],
            'deployed_code': history_df['deployed_code'].iloc[0],
            'closed_tickets': history_df['closed_tickets'].iloc[0],
        }
        
        fig = self.create_static_diagram(initial_stocks)
        
        # Create frames for animation
        frames = []
        for i in range(len(history_df)):
            stocks = {
                'open_tickets': history_df['open_tickets'].iloc[i],
                'started_coding': history_df['started_coding'].iloc[i],
                'tested_code': history_df['tested_code'].iloc[i],
                'deployed_code': history_df['deployed_code'].iloc[i],
                'closed_tickets': history_df['closed_tickets'].iloc[i],
            }
            
            flows = {}
            if i < len(flow_history_df):
                flows = {
                    'start_coding_flow': flow_history_df['start_coding_flow'].iloc[i],
                    'testing_flow': flow_history_df['testing_flow'].iloc[i],
                    'deployment_flow': flow_history_df['deployment_flow'].iloc[i],
                    'closing_flow': flow_history_df['closing_flow'].iloc[i],
                    'testing_error_flow': flow_history_df['testing_error_flow'].iloc[i],
                    'deployment_error_flow': flow_history_df['deployment_error_flow'].iloc[i],
                    'production_error_flow': flow_history_df['production_error_flow'].iloc[i],
                }
            
            frame_fig = self.create_static_diagram(stocks, flows)
            
            frames.append(go.Frame(
                data=frame_fig.data,
                layout=frame_fig.layout,
                name=f"frame_{i}",
                traces=list(range(len(frame_fig.data)))
            ))
        
        fig.frames = frames
        
        # Add play/pause buttons
        fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 100, 'redraw': True},
                            'fromcurrent': True,
                            'mode': 'immediate',
                            'transition': {'duration': 50}
                        }]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ],
                'x': 0.1,
                'y': -0.05,
                'xanchor': 'left',
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'steps': [
                    {
                        'args': [[f"frame_{i}"], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': f"{i}",
                        'method': 'animate'
                    }
                    for i in range(len(frames))
                ],
                'x': 0.1,
                'y': -0.15,
                'len': 0.9,
                'xanchor': 'left',
                'yanchor': 'top'
            }]
        )
        
        return fig
    
    def _add_arrow(
        self, 
        fig: go.Figure, 
        x0: float, 
        y0: float, 
        x1: float, 
        y1: float, 
        color: str,
        label: str = None
    ):
        """Add a straight arrow to the figure."""
        fig.add_annotation(
            x=x1, y=y1,
            ax=x0, ay=y0,
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=color,
            text=label if label else "",
            font=dict(size=9, color=color),
            yshift=10 if label else 0,
        )
    
    def _add_curved_arrow(
        self,
        fig: go.Figure,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        color: str,
        label: str = None,
        offset: float = 0.5
    ):
        """Add a curved arrow (for backward error flows)."""
        # Create curved path
        mid_x = (x0 + x1) / 2
        mid_y = max(y0, y1) + offset
        
        # Bezier curve points
        t = np.linspace(0, 1, 50)
        x = (1-t)**2 * x0 + 2*(1-t)*t * mid_x + t**2 * x1
        y = (1-t)**2 * y0 + 2*(1-t)*t * mid_y + t**2 * y1
        
        # Add the curve
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            line=dict(color=color, width=2, dash='dash'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add arrowhead at the end
        fig.add_annotation(
            x=x1, y=y1,
            ax=x[-5], ay=y[-5],
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor=color,
            text="",
        )
        
        # Add label at the peak
        if label:
            fig.add_annotation(
                x=mid_x, y=mid_y,
                text=label,
                showarrow=False,
                font=dict(size=9, color=color),
            )
    
    def _add_flow_annotations(self, fig: go.Figure, flows: Dict[str, float]):
        """Add small annotations showing flow values."""
        # Only show non-zero flows to avoid clutter
        flow_positions = {
            'start_coding_flow': (1, 1.7),
            'testing_flow': (3, 1.7),
            'deployment_flow': (5, 1.7),
            'closing_flow': (7, 1.7),
        }
        
        for flow_name, (x, y) in flow_positions.items():
            value = flows.get(flow_name, 0)
            if value > 0:
                fig.add_annotation(
                    x=x, y=y,
                    text=f"{int(value)}",
                    showarrow=False,
                    font=dict(size=10, color=self.COLOR_FORWARD_FLOW),
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    borderpad=2,
                )

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List

def create_reward_timeline(history: List[Dict]) -> go.Figure:
    """Create cumulative reward timeline"""
    df = pd.DataFrame(history)
    
    fig = go.Figure()
    
    # Cumulative reward
    fig.add_trace(go.Scatter(
        x=df['iteration'],
        y=df['cumulative_reward'],
        mode='lines',
        name='Cumulative Reward',
        line=dict(color='#1f77b4', width=3)
    ))
    
    # Average reward (moving average)
    window = min(50, len(df) // 10)
    if window > 1:
        df['avg_reward_ma'] = df['average_reward'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(
            x=df['iteration'],
            y=df['avg_reward_ma'],
            mode='lines',
            name=f'Avg Reward (MA-{window})',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title="Reward Evolution Over Time",
        xaxis_title="Iteration",
        yaxis_title="Reward",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_arm_comparison(stats: Dict, true_rates: List[float] = None) -> go.Figure:
    """Create arm comparison chart"""
    arms = stats['arm_names']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Arm Pull Distribution', 'Estimated vs True Value'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Pull distribution
    fig.add_trace(
        go.Bar(
            x=arms,
            y=stats['arm_counts'],
            name='Pulls',
            marker_color='#2ca02c',
            text=stats['arm_counts'],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Value comparison
    fig.add_trace(
        go.Bar(
            x=arms,
            y=stats['arm_values'],
            name='Estimated',
            marker_color='#1f77b4',
            text=[f"{v:.4f}" for v in stats['arm_values']],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    if true_rates:
        fig.add_trace(
            go.Bar(
                x=arms,
                y=true_rates,
                name='True Value',
                marker_color='#d62728',
                opacity=0.6,
                text=[f"{v:.4f}" for v in true_rates],
                textposition='outside'
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        barmode='group'
    )
    
    return fig

def create_regret_plot(history: List[Dict], optimal_reward: float) -> go.Figure:
    """Create cumulative regret plot"""
    df = pd.DataFrame(history)
    
    # Calculate regret
    df['optimal_cumulative'] = optimal_reward * df['iteration']
    df['regret'] = df['optimal_cumulative'] - df['cumulative_reward']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['iteration'],
        y=df['regret'],
        mode='lines',
        name='Cumulative Regret',
        line=dict(color='#d62728', width=3),
        fill='tozeroy',
        fillcolor='rgba(214, 39, 40, 0.2)'
    ))
    
    fig.update_layout(
        title="Cumulative Regret (Lower is Better)",
        xaxis_title="Iteration",
        yaxis_title="Regret",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_arm_evolution(history: List[Dict], arm_names: List[str]) -> go.Figure:
    """Create arm selection evolution over time"""
    df = pd.DataFrame(history)
    
    fig = go.Figure()
    
    for i, arm in enumerate(arm_names):
        # Extract counts for this arm
        counts = [h['arm_counts'][i] for h in history]
        
        fig.add_trace(go.Scatter(
            x=df['iteration'],
            y=counts,
            mode='lines',
            name=arm,
            line=dict(width=2),
            stackgroup='one'
        ))
    
    fig.update_layout(
        title="Arm Selection Evolution (Cumulative Pulls)",
        xaxis_title="Iteration",
        yaxis_title="Cumulative Pulls",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_confidence_intervals(stats: Dict) -> go.Figure:
    """Create confidence interval visualization for arm values"""
    arms = stats['arm_names']
    values = stats['arm_values']
    counts = stats['arm_counts']
    
    # Calculate 95% confidence intervals (assuming Bernoulli)
    ci_lower = []
    ci_upper = []
    
    for value, count in zip(values, counts):
        if count > 0:
            se = np.sqrt(value * (1 - value) / count)
            ci_lower.append(max(0, value - 1.96 * se))
            ci_upper.append(min(1, value + 1.96 * se))
        else:
            ci_lower.append(0)
            ci_upper.append(1)
    
    fig = go.Figure()
    
    # Add confidence intervals
    for i, arm in enumerate(arms):
        fig.add_trace(go.Scatter(
            x=[arm, arm],
            y=[ci_lower[i], ci_upper[i]],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))
    
    # Add point estimates
    fig.add_trace(go.Scatter(
        x=arms,
        y=values,
        mode='markers',
        marker=dict(size=12, color='#1f77b4'),
        name='Estimated Value',
        text=[f"{v:.4f}<br>n={int(c)}" for v, c in zip(values, counts)],
        hovertemplate='%{x}<br>Value: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Arm Value Estimates with 95% Confidence Intervals",
        xaxis_title="Arm",
        yaxis_title="Estimated Conversion Rate",
        height=400,
        yaxis_range=[0, 1]
    )
    
    return fig

def create_metrics_summary(stats: Dict) -> go.Figure:
    """Create summary metrics visualization"""
    fig = go.Figure()
    
    metrics = [
        ("Total Pulls", stats['total_pulls']),
        ("Avg Reward", f"{stats['average_reward']:.4f}"),
        ("Total Reward", f"{stats['total_reward']:.2f}"),
        ("Active Arms", sum(1 for c in stats['arm_counts'] if c > 0))
    ]
    
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd']
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Metric', 'Value'],
            fill_color='#1f77b4',
            font=dict(color='white', size=14),
            align='left'
        ),
        cells=dict(
            values=[[m[0] for m in metrics], [m[1] for m in metrics]],
            fill_color='lavender',
            font=dict(size=12),
            align='left',
            height=30
        )
    )])
    
    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
    
    return fig
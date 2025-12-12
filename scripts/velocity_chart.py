#!/usr/bin/env python3
"""
Standalone script to generate velocity chart for sprint planning.

Generates a grouped bar chart showing planned vs completed story points per sprint.
Saves the chart as docs/velocity.png.

Usage:
    python3 scripts/velocity_chart.py
"""

import matplotlib.pyplot as plt
from pathlib import Path

# Hardcoded sprint data (4 sprints)
sprint_data = [
    {"sprint": "Sprint 1", "planned": 20, "completed": 18},
    {"sprint": "Sprint 2", "planned": 22, "completed": 20},
    {"sprint": "Sprint 3", "planned": 25, "completed": 23},
    {"sprint": "Sprint 4", "planned": 24, "completed": 24},
]

def main():
    # Extract data
    sprints = [item["sprint"] for item in sprint_data]
    planned = [item["planned"] for item in sprint_data]
    completed = [item["completed"] for item in sprint_data]
    
    # Calculate velocity (completion rate) per sprint
    velocities = []
    print("\nSprint Velocity:")
    print("-" * 50)
    for item in sprint_data:
        velocity = (item["completed"] / item["planned"] * 100) if item["planned"] > 0 else 0
        velocities.append(velocity)
        print(f"{item['sprint']}: {item['completed']}/{item['planned']} = {velocity:.1f}%")
    print("-" * 50)
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up bar positions
    x = range(len(sprints))
    width = 0.35
    
    # Create grouped bars
    bars1 = ax.bar([i - width/2 for i in x], planned, width, label='Planned', color='#3498db', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], completed, width, label='Completed', color='#2ecc71', alpha=0.8)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
    
    # Customize the chart
    ax.set_xlabel('Sprint', fontsize=12, fontweight='bold')
    ax.set_ylabel('Story Points', fontsize=12, fontweight='bold')
    ax.set_title('Sprint Velocity: Planned vs Completed', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(sprints)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Set y-axis to start from 0
    ax.set_ylim(bottom=0)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Ensure docs directory exists
    docs_dir = Path(__file__).parent.parent / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # Save the chart
    output_path = docs_dir / 'velocity.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nChart saved to: {output_path}")
    
    # Close the figure to free memory
    plt.close()

if __name__ == '__main__':
    main()


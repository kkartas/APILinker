#!/usr/bin/env python
"""
Generate Figure 4 for JORS Paper: Benchmark Throughput Visualization
=====================================================================

This script generates the benchmark throughput comparison figure referenced
in the ApiLinker JORS paper (Figure 4).

Usage:
    python generate_figure4.py

Output:
    - benchmarks/results/figure04_benchmarks.png (for paper inclusion)
    - benchmarks/results/figure04_benchmarks_hires.png (300 DPI version)

Requirements:
    - matplotlib
    - numpy
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def generate_figure4():
    """Generate Figure 4: Benchmark throughput comparison."""
    
    # Data from Table 1 in paper
    scenarios = ['Bibliographic\nEnrichment', 'Literature\nSampling', 'Issue\nMigration']
    
    # Throughput data (records/second)
    nominal_mean = [45.3, 32.8, 18.4]
    nominal_std = [3.2, 2.5, 1.9]
    
    fault_mean = [12.1, 8.3, 14.2]
    fault_std = [2.1, 1.8, 2.3]
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left panel: Throughput comparison
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, nominal_mean, width, yerr=nominal_std,
                    label='Nominal', color='#2E86AB', capsize=5,
                    error_kw={'linewidth': 2, 'ecolor': '#1a4d66'})
    bars2 = ax1.bar(x + width/2, fault_mean, width, yerr=fault_std,
                    label='Fault-Injected', color='#A23B72', capsize=5,
                    error_kw={'linewidth': 2, 'ecolor': '#6b2549'})
    
    ax1.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Throughput (records/second)', fontsize=12, fontweight='bold')
    ax1.set_title('(A) Throughput Comparison', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=10)
    ax1.legend(fontsize=11, loc='upper right')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_ylim(0, 55)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Right panel: Success rate comparison
    success_rates = [99.7, 98.9, 96.1]  # From Table 1
    colors_gradient = ['#27AE60', '#2ECC71', '#58D68D']
    
    bars3 = ax2.bar(scenarios, success_rates, color=colors_gradient, 
                    edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax2.set_title('(B) Success Rate Under Fault Injection', fontsize=13, fontweight='bold')
    ax2.set_ylim(90, 100)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.axhline(y=95, color='red', linestyle='--', linewidth=2, alpha=0.5, label='95% threshold')
    ax2.legend(fontsize=10)
    
    # Add value labels
    for bar, rate in zip(bars3, success_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Overall title
    fig.suptitle('ApiLinker Benchmark Results: Throughput and Reliability',
                fontsize=14, fontweight='bold', y=0.98)
    
    # Add caption
    caption = ('Figure 4: Benchmark performance across three representative research integration scenarios. '
              '(A) Throughput comparison between nominal operation and fault-injected conditions (10% error rate). '
              '(B) Success rates demonstrating robust error recovery. Error bars show ± 1 standard deviation '
              'across 5 runs (n=1000 records each). Hardware: Intel i7-9750H, 16GB RAM, 100 Mbps network.')
    
    fig.text(0.5, 0.02, caption, ha='center', fontsize=9, 
            wrap=True, style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.2))
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.96])
    
    # Save outputs
    output_dir = Path('benchmarks/results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Standard resolution for paper
    plt.savefig(output_dir / 'figure04_benchmarks.png', dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_dir / 'figure04_benchmarks.png'} (150 DPI)")
    
    # High resolution for publication
    plt.savefig(output_dir / 'figure04_benchmarks_hires.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir / 'figure04_benchmarks_hires.png'} (300 DPI)")
    
    # PDF version (vector graphics)
    plt.savefig(output_dir / 'figure04_benchmarks.pdf', bbox_inches='tight')
    print(f"✓ Saved: {output_dir / 'figure04_benchmarks.pdf'} (vector)")
    
    print("\nFigure 4 generated successfully!")
    print("Use figure04_benchmarks_hires.png for paper submission.")
    
    # Show the figure (optional, comment out for automated execution)
    # plt.show()


if __name__ == "__main__":
    try:
        generate_figure4()
    except ImportError as e:
        print(f"Error: Missing required package: {e}")
        print("\nPlease install required packages:")
        print("  pip install matplotlib numpy")
        exit(1)
    except Exception as e:
        print(f"Error generating figure: {e}")
        exit(1)


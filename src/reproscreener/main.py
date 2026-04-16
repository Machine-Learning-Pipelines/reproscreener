import sqlite3
from reproscreener.reprodb import MetricSetManager


def main():
    # Initialize
    conn = sqlite3.connect('reproscreener.db')
    manager = MetricSetManager(conn)

    # 1. Create metrics
    manager.add_metric('code_available', 'Code Available', 'repository')
    manager.add_metric('dependencies', 'Software Dependencies', 'repository')
    manager.add_metric('dataset', 'Dataset', 'paper')
    manager.add_metric('hypothesis', 'Hypothesis', 'paper')
    manager.add_metric('problem', 'Problem Statement', 'paper')

    # 2. Create metric sets
    manager.create_metric_set('basic', 'Basic Check', 'Quick reproducibility check')
    manager.create_metric_set('comprehensive', 'Full Analysis', 'Complete evaluation')

    # 3. Add metrics to sets
    # Method 1: Add one at a time with specific positions
    manager.add_metric_to_set('basic', 'code_available', 1)
    manager.add_metric_to_set('basic', 'dependencies', 2)

    # Method 2: Add multiple at once (auto-positions)
    manager.add_multiple_metrics_to_set('comprehensive', [
        'problem', 'hypothesis', 'dataset', 'code_available', 'dependencies'
    ])

    # 4. Query relationships
    # Get all metrics in the 'basic' set
    basic_metrics = manager.get_metrics_in_set('basic')
    print("Basic set contains:", [m['display_name'] for m in basic_metrics])

    # Find which sets contain 'code_available'
    sets_with_code = manager.get_sets_containing_metric('code_available')
    print("'code_available' appears in:", [s['set_name'] for s in sets_with_code])

    # 5. Modify relationships
    # Remove a metric from a set
    manager.remove_metric_from_set('basic', 'dependencies')

    # Reorder a metric within a set
    manager.reorder_metric_in_set('comprehensive', 'dataset', 1)  # Move to position 1

    # 6. Get overview matrix
    matrix = manager.get_comparison_matrix()
    print("\nMetric-Set Matrix:")
    print(matrix)

if __name__ == "__main__":
    main()
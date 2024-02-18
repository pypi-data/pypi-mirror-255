import matplotlib.pyplot as plt
import pandas as pd


#########################################
#             Histogram graph           #
#########################################
def graph_multiple_histograms(df, columns, layout=(2, 2), bin_numbers=None):
    """
    Plot multiple histograms of specified columns from a DataFrame.

        :param df: The pandas DataFrame containing the data.
        :type df: pandas.DataFrame
        
        :param columns: List of column names to be plotted.
        :type columns: list
        
        :param layout: Tuple specifying the layout dimensions of subplots. Default is (2, 2).
        :type layout: tuple, optional
        
        :param bin_numbers: List of integers specifying the number of bins for each column.
        :type bin_numbers: list, optional
    
    Example:
    
    .. code-block:: python

        from quick_anomaly_detector.data_process import graph_multiple_histograms
        
        columns_to_plot = ['a', 'b', 'c', 'd']
        bin_numbers = [10, 20, 15, 10]  # Example list of bin numbers corresponding to each column
        fig = graph_multiple_histograms(df, columns_to_plot, layout=(2, 2), bin_numbers=bin_numbers)
        plt.show()
    
    """
    num_plots = len(columns)
    num_rows, num_cols = layout
    total_plots = num_rows * num_cols

    if num_plots > total_plots:
        raise ValueError("Number of columns exceeds the available space in the layout.")

    if bin_numbers is None:
        bin_numbers = [10] * num_plots
    elif len(bin_numbers) != num_plots:
        raise ValueError("Length of bin_numbers must match the number of columns.")

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(14, 10))
    axes = axes.ravel()

    for i, (column, bins) in enumerate(zip(columns, bin_numbers)):
        ax = axes[i]
        ax.hist(df[column], bins=bins)
        ax.set_xlabel(column)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {column}")

    # Hide empty subplots
    for j in range(num_plots, total_plots):
        axes[j].axis('off')

    plt.tight_layout()
    return fig
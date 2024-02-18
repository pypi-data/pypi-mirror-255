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




#########################################
#             Histogram graph           #
#########################################
def apply_transformations(df, column_name):
    """
    Apply logarithm and square transformations to a column in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the column to transform.
    column_name : str
        The name of the column to transform.

    Returns
    -------
    list
        A list of column names including the original column and the transformed columns.
    
        
    Example

    .. code-block:: python

        from quick_anomaly_detector.data_process import apply_transformations

        columns_to_plot = log_sqaure(df, 'column_name')
    """
    # Apply transformations
    df[f'log_{column_name}'] = df[column_name].apply(lambda x: np.log(x + 0.001))
    df[f'square2_{column_name}'] = df[column_name].apply(lambda x: x ** 2)
    df[f'square0.5_{column_name}'] = df[column_name].apply(lambda x: x ** 0.5)
    
    # Define columns to plot
    transformed_columns = [column_name, f'log_{column_name}', f'square2_{column_name}', f'square0.5_{column_name}']
    
    return transformed_columns
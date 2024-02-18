import matplotlib.pyplot as plt
import pandas as pd


#########################################
#             Histogram graph           #
#########################################
def graph_histogram(df, x_column, bin_number=10):
    """
    Plot a histogram of a specified column from a DataFrame.

    Parameters:
    - df (DataFrame): The pandas DataFrame containing the data.
    - x_column (str): The name of the column to be plotted.
    - bin_number (int, optional): The number of bins to use for the histogram. Default is 10.

    Returns:
    - fig (matplotlib.figure.Figure): The matplotlib Figure object containing the histogram plot.

    Example:
    >>> import pandas as pd
    >>> import matplotlib.pyplot as plt
    >>> df = pd.DataFrame({'age': [25, 30, 35, 40, 45, 50]})
    >>> fig = graph_histogram(df, 'age', bin_number=5)
    >>> plt.show()
    """
    fig, ax = plt.subplots()
    ax.hist(df[x_column], bins=bin_number)
    ax.set_xlabel(x_column)
    ax.set_ylabel("Frequency")
    ax.set_title(f"Histogram of {x_column}")
    return fig
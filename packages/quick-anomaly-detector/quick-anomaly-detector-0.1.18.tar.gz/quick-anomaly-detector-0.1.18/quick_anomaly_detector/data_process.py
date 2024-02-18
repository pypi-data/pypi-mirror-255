import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
import pandas as pd
import numpy as np
import torch

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



##################################################
#                Scatter graph                   #
##################################################
def graph_scatter(df, x_column, y_column, color_column):
    """
    Create a scatter plot with color mapping based on a column of a DataFrame.

    :param df: The pandas DataFrame containing the data.
    :type df: pandas.DataFrame

    :return: The generated scatter plot figure.
    :rtype: matplotlib.figure.Figure

    :raises ValueError: If one or more specified columns do not exist in the DataFrame.

    Example: 

    .. code-block:: python

        from quick_anomaly_detector.data_process import graph_scatter

        df = pd.DataFrame({'x_column': [1, 2, 3], 'y_column': [4, 5, 6], 'color_column': ['red', 'blue', 'green']})
        fig = graph_scatter(df, 'x_column', 'y_column', 'color_column')
        plt.show()
    
    .. note:: 
    
        Ensure that the DataFrame contains the required columns for plotting.
    """
    # Validate input parameters
    if not all(col in df.columns for col in [x_column, y_column, color_column]):
        raise ValueError("One or more specified columns do not exist in the DataFrame.")

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(df[x_column], df[y_column], c=df[color_column], cmap='viridis', alpha=0.7)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f"Scatter Chart (Color by {color_column})")
    cbar = plt.colorbar(ScalarMappable(norm=None, cmap='viridis'), ax=ax, label=color_column)
    return fig




##################################################
#         Log Sqaure feature transform           #
##################################################
def apply_transformations(df, column_name):
    """
    Apply logarithm and square transformations to a column in a DataFrame.

    :param df: The pandas DataFrame containing the data.
    :type df: pandas.DataFrame
        
    :param column_name: The name of the column to transform.
    :type column_name: str

    :return: A list of column names including the original column and the transformed columns.
    :rtype: list
        
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



##################################################
#         check valid tensor                     #
##################################################
def check_valid_tensor_data(input_tensor):
    """
    Perform checks on the input tensor.
    
    :param input_tensor: Input tensor to be checked.
    :type input_tensor: torch.Tensor
    
    :return: True if input passes all checks, False otherwise.
    :rtype: bool
    
    :return: Message indicating the result of the checks.
    :rtype: str
    
    Example: 

    .. code-block:: python

        from quick_anomaly_detector.data_process import check_valid_tensor_data

        input_tensor = torch.tensor([1.0, 2.0, float('nan'), 4.0])  # Example tensor with NaN
        valid, message = check_valid_tensor_data(input_tensor)
        print(valid, message)
    """
    # Check if input_tensor is a torch.Tensor
    if not isinstance(input_tensor, torch.Tensor):
        return False, "Input is not a torch.Tensor"
    
    # Check if input_tensor contains NaN or infinite values
    if torch.isnan(input_tensor).any() or torch.isinf(input_tensor).any():
        return False, "Input contains NaN or infinite values"
    
    # Check if input_tensor is of floating-point data type
    if input_tensor.dtype not in [torch.float32, torch.float64]:
        return False, "Input is not of floating-point data type"
    
    # Check if input_tensor has a valid shape (not empty)
    if input_tensor.numel() == 0:
        return False, "Input tensor has an empty shape"
    
    return True, "Input passes all checks"



#########################################################
#         Customeized Imputer Class                     #
#########################################################
from sklearn.base import TransformerMixin
from sklearn.impute import SimpleImputer

class CustomImputer(TransformerMixin):
    """
    A custom imputer transformer that extends scikit-learn's SimpleImputer
    while preserving column names after imputation.

    Parameters
    ----------
    strategy : {'mean', 'median', 'most_frequent', 'constant'}, default='mean'   
        The imputation strategy.   
    fill_value : str, int, or float, optional    
        The constant value to fill missing values when strategy='constant'.

    Attributes
    ----------
    strategy : str   
        The imputation strategy.
    fill_value : str, int, or float   
        The constant value to fill missing values when strategy='constant'.

    Methods
    -------
    fit(X, y=None)   
        Fit the imputer to the data.
    transform(X, y=None)   
        Transform the data by imputing missing values and preserving column names.

    Examples

        .. code-block:: python
    
        from sklearn.pipeline import Pipeline
        quick_anomaly_detector.data_process import CustomImputer

        fill_values = {
            'column1': 0,
            'column2': ''
        }
        pipeline = Pipeline([
            ('imputer', CustomImputer(strategy='mean')),
            ('fillna', CustomImputer(strategy='constant', fill_value=fill_values)),
        ])
        X_train_imputed = pipeline.fit_transform(X_train)

    """
    def __init__(self, strategy='mean', fill_value=None):
        self.strategy = strategy
        self.fill_value = fill_value
        self.imputer = SimpleImputer(strategy=strategy, fill_value=fill_value)

    def fit(self, X, y=None):
        """
        Fit the imputer to the data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data.

        y : array-like of shape (n_samples,), default=None
            Ignored.

        Returns
        -------
        self : object
            Returns self.
        """
        self.imputer.fit(X)
        return self

    def transform(self, X, y=None):
        """
        Transform the data by imputing missing values and preserving column names.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data.

        y : array-like of shape (n_samples,), default=None
            Ignored.

        Returns
        -------
        X_imputed : pandas.DataFrame of shape (n_samples, n_features)
            The transformed data with imputed missing values and preserved column names.
        """
        X_imputed = self.imputer.transform(X)
        # Restore column names
        X_imputed = pd.DataFrame(X_imputed, columns=X.columns)
        return X_imputed
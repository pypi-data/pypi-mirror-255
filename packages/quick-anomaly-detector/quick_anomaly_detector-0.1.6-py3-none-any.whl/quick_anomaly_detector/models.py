import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal

#########################################
#   Gaussian Based Anomaly Detection    #
#########################################
# select epsilon base on F1
class AnomalyDetectionModel:
    """
    Anomaly Detection Model using Gaussian Distribution.

    This class provides a simple implementation of an anomaly detection model
    based on the Gaussian distribution. It includes methods for estimating
    Gaussian parameters, calculating p-values, selecting the threshold, and making predictions.

    Attributes:
        - **mu_train** (*ndarray*): Mean vector of the training data.
        - **var_train** (*ndarray*): Variance vector of the training data.
        - **p_values_train** (*ndarray*): P-values for training data.
        - **p_values_val** (*ndarray*): P-values for validation data.
        - **epsilon** (*float*): Chosen threshold for anomaly detection.
        - **f1** (*float*): F1 score corresponding to the chosen threshold.

    Example:
    
    .. code-block:: python

        from quick_anomaly_detector.models import AnomalyDetectionModel

        # Load your datasets (X_train, X_val, y_val)
        # ...

        # Create an instance of AnomalyDetectionModel
        model = AnomalyDetectionModel()

        # Train the model
        model.train(X_train, X_val, y_val)

        # Predict anomalies in the validation dataset
        anomalies = model.predict(X_val)

        print(anomalies)

    .. note::
        The anomaly detection model assumes that the input data follows a Gaussian distribution.

    .. warning::
        This class is designed for educational purposes and may not be suitable for all types of data.
    """

    def __init__(self):
        """
        Initialize the AnomalyDetectionModel.
        """
        self.mu_train = 0
        self.var_train = 0
        self.p_values_train = 0
        self.p_values_val = 0
        self.epsilon = 0.05
        self.f1 = 0
    
    def estimate_gaussian(self, X):
        m, n = X.shape
        mu = np.mean(X, axis=0)
        var = np.var(X, axis=0)
        return mu, var
    
    def calculate_p_value(self, X, mu, var):
        mvn = multivariate_normal(mean=mu, cov=np.diag(var))
        p_values = mvn.pdf(X)
        return p_values
    
    def select_threshold(self, y_val, p_val): 
        best_epsilon = 0
        best_F1 = 0
        F1 = 0
        step_size = (max(p_val) - min(p_val)) / 1000
        for epsilon in np.arange(min(p_val), max(p_val), step_size):
            predictions = (p_val < epsilon).astype(int)
            tp = np.sum((predictions == 1) & (y_val == 1))
            fp = np.sum((predictions == 1) & (y_val == 0))
            fn = np.sum((predictions == 0) & (y_val == 1))
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            F1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            if F1 > best_F1:
                best_F1 = F1
                best_epsilon = epsilon
        return best_epsilon, best_F1
    

    def train(self, X_train, X_val, y_val):
        """
        Train the AnomalyDetectionModel.

            :param X_train: Training data matrix.
            :type X_train: ndarray

            :param X_val: Validation data matrix.
            :type X_val: ndarray

            :param y_val: Ground truth labels for validation data.
            :type y_val: ndarray
        """
        self.mu_train, self.var_train = self.estimate_gaussian(X_train)
        self.p_values_train = self.calculate_p_value(X_train, self.mu_train, self.var_train)
        self.p_values_val = self.calculate_p_value(X_val, self.mu_train, self.var_train)
        self.epsilon, self.f1 = self.select_threshold(y_val, self.p_values_val)

    def predict(self, X):
        """
        Predict outliers in the input data.

        Parameters:
            :param X: Input data matrix.
            :type X: ndarray

        Returns:
            :return: Boolean array indicating whether each sample is an outlier.
            :rtype: ndarray
        """
        p_values = self.calculate_p_value(X, self.mu_train, self.var_train)
        outliers = p_values < self.epsilon
        return outliers



#########################################
#          K-Means Cluster              #
#########################################
class KMeansModel:
    """
    KMeansModel

    The `KMeansModel` class is a Python implementation of the K-means clustering algorithm. Clustering is a type of unsupervised machine learning that partitions data into groups (clusters) based on similarity. The K-means algorithm aims to divide the data into K clusters, where each cluster is represented by its centroid.

    To use the `KMeansModel` class, follow these steps:

    1. Create an instance of the class with an optional parameter `K` (number of clusters, default is 3).

    .. code-block:: python

        from quick_anomaly_detector.models import KMeansModel

        kmeans = KMeansModel(K=3)

    2. Train the model on your data using the `train` method.

    .. code-block:: python

        centroids, labels = kmeans.train(X, max_iters=10)

    - `X`: Input data matrix.
    - `max_iters`: Maximum number of iterations for the K-means algorithm (default is 10).

    3. Access the resulting centroids and labels.

    .. code-block:: python

        centroids = kmeans.centroids
        labels = kmeans.labels

    4. Optionally, perform image compression using the `image_compression` method.

    .. code-block:: python

        compressed_img = kmeans.image_compression(image_path, color_K=16, max_iters=10)

    """

    def __init__(self, K=3):
        """
        Initialize a KMeansModel instance.

        Parameters:
            K (int): Number of centroids (clusters). Default is 3.
        """
        self.K = K

    def kMeans_init_centroids(self, X, K):
        """
        Randomly initialize centroids.

        Parameters:
            X (ndarray): Input data matrix.
            K (int): Number of centroids.

        Returns:
            ndarray: Initialized centroids.
        """
        randidx = np.random.permutation(X.shape[0])
        centroids = X[randidx[:K]]
        return centroids

    def find_closest_centroids(self, X, centroids):
        """
        Find the closest centroid for each example.

        Parameters:
            X (ndarray): Input data matrix.
            centroids (ndarray): Current centroids.

        Returns:
            ndarray: Index of the closest centroid for each example.
        """
        K = centroids.shape[0]
        idx = np.zeros(X.shape[0], dtype=int)
        for i in range(X.shape[0]):
            distances = np.linalg.norm(X[i] - centroids, axis=1)
            idx[i] = np.argmin(distances)
        return idx

    def compute_centroids(self, X, idx, K):
        """
        Compute new centroids based on assigned examples.

        Parameters:
            X (ndarray): Input data matrix.
            idx (ndarray): Index of the closest centroid for each example.
            K (int): Number of centroids.

        Returns:
            ndarray: New centroids.
        """
        m, n = X.shape
        centroids = np.zeros((K, n))
        for k in range(K):
            indices = (idx == k)
            centroids[k, :] = np.mean(X[indices, :], axis=0)
        return centroids

    def train(self, X, K=3, max_iters=10):
        """
        Train the KMeansModel.

        Parameters:
            X (ndarray): Input data matrix.
            K (int): Number of centroids (clusters). Default is 3.
            max_iters (int): Maximum number of iterations. Default is 10.

        Returns:
            tuple: Resulting centroids and index of each data point's assigned cluster.
        """
        initial_centroids = self.kMeans_init_centroids(X, K)
        m, n = X.shape
        K = initial_centroids.shape[0]
        centroids = initial_centroids
        previous_centroids = centroids  
        idx = np.zeros(m)  
        for i in range(max_iters):
            idx = self.find_closest_centroids(X, centroids)
            centroids = self.compute_centroids(X, idx, K)
        return centroids, idx
    
    def image_compression(self, image_path, color_K=16, max_iters=10):
        """
        Perform image compression using K-means clustering.

        Parameters:
            image_path (str): Path to the input image file.
            color_K (int): Number of colors for compression. Default is 16.
            max_iters (int): Maximum number of iterations for K-means. Default is 10.

        Returns:
            ndarray: Compressed image.
        """
        original_img = plt.imread(image_path)
        X_img = np.reshape(original_img, (original_img.shape[0] * original_img.shape[1], 4))
        centroids, idx = self.train(X_img, color_K, max_iters)
        X_recovered = centroids[idx, :]
        X_recovered = np.reshape(X_recovered, original_img.shape)
        return X_recovered






        
    

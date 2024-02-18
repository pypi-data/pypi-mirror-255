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
#      NN Based Anomaly Detection       #
#########################################
import torch
import torch.nn as nn
class AnomalyDetectionNN(nn.Module):
    """
    AnomalyDetectionNN is a neural network model designed for anomaly detection tasks.

    It consists of three fully connected layers:
    - Input layer: Takes input data with a shape of (batch_size, input_dim).
    - Hidden layer 1: Consists of 64 neurons and applies ReLU activation function.
    - Hidden layer 2: Consists of 32 neurons and applies ReLU activation function.
    - Output layer: Consists of input_dim neurons, representing the reconstructed data.
      It applies the sigmoid activation function to squash the output values between 0 and 1.

    Parameters:
        input_dim (int): The number of features in the input data.

    Attributes:
        fc1 (nn.Linear): The first fully connected layer.
        fc2 (nn.Linear): The second fully connected layer.
        fc3 (nn.Linear): The output layer.

    Methods:
        forward(x): Forward pass through the neural network.
    
    Example:

    .. code-block:: python

        from quick_anomaly_detector.models import AnomalyDetectionNN

        # Load your datasets (X_train, X_val)
        # ...
        
        # normalization
        min_vals = np.min(X_train, axis=0)
        max_vals = np.max(X_train, axis=0)
        normalized_training_data = (X_train - min_vals) / (max_vals - min_vals)
        normalized_validation_data = (X_valid - min_vals) / (max_vals - min_vals)
        input_dim = normalized_training_data.shape[1]

        # Create an instance of AnomalyDetectionModel
        model = AnomalyDetectionNN(input_dim)

        # Train the model
        X_train_tensor = torch.tensor(normalized_training_data, dtype=torch.float32)
        train_dataset = TensorDataset(X_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

        X_valid_tensor = torch.tensor(normalized_validation_data, dtype=torch.float32)
        valid_dataset = TensorDataset(X_valid_tensor)
        valid_loader = DataLoader(valid_dataset, batch_size=64, shuffle=False)

        optimizer = optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        # train ...


    """
    def __init__(self, input_dim, min_vals = None, max_vals = None):
        """
        Initialize the AnomalyDetectionNN model.

        Args:
            input_dim (int): The number of features in the input data.
            min_vals (list): Min values of each feature in train data.
            max_vals (list): Max values of each feature in train data.
        """
        super(AnomalyDetectionNN, self).__init__()
        self.min_vals = min_vals
        self.max_vals = max_vals
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, input_dim)  # same as input, for loss calculation

    def forward(self, x):
        """
        Perform the forward pass through the neural network.

        Args:
            x (torch.Tensor): The input data tensor with shape (batch_size, input_dim).

        Returns:
            torch.Tensor: The reconstructed output tensor with the same shape as the input.
        """
        x = self.fc1(x)   # input shape is (1, N, M), N is samples number, M is feaures number
        x = torch.relu(x)
        x = self.fc2(x)
        x = torch.relu(x)
        x = self.fc3(x)
        x = torch.sigmoid(x)  # Apply sigmoid activation to squash output between 0 and 1
        return x
    

################################################
#          Train Anomaly NN model              #
################################################
from torch.utils.data import DataLoader, TensorDataset
import torch.optim as optim
from .data_process import check_valid_tensor_data


class TrainAnomalyNN:
    """
    Class for training and using an anomaly detection neural network.

    Attributes:
    - lr (float): The learning rate for optimization (default: 0.001).
    - num_epochs (int): The maximum number of training epochs (default: 1000).
    - patience (int): The number of epochs to wait before early stopping if validation loss does not improve (default: 10).
    - model (AnomalyDetectionNN): The trained anomaly detection neural network model.
    - optimizer (torch.optim.Optimizer): The optimizer used for training.
    - criterion (torch.nn.Module): The loss function used for training.
    - train_min_values (numpy.ndarray): The minimum values of each feature in the training dataset.
    - train_max_values (numpy.ndarray): The maximum values of each feature in the training dataset.

    Example:
    
    .. code-block:: python

        from quick_anomaly_detector.models import TrainAnomalyNN

        train_model = TrainAnomalyNN(lr=0.001, num_epochs=1000, patience=10)
        train_model.train(X_train, X_valid)
        predict_result = train_model.predict(X_valid, threshold = 0.0002)

    """
    def __init__(self, lr=0.001, num_epochs=1000, patience=10):
        """
        Initializes the TrainAnomalyNN class.

        Args:
        - lr (float): The learning rate for optimization (default: 0.001).
        - num_epochs (int): The maximum number of training epochs (default: 1000).
        - patience (int): The number of epochs to wait before early stopping if validation loss does not improve (default: 10).
        """
        self.input_dim = None
        self.lr = lr
        self.num_epochs = num_epochs
        self.patience = patience
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.train_min_values = None
        self.train_max_values = None
    
    def _normalize_data(self, X, isValid=False):
        """
        Normalizes the input data.

        Args:
        - X (numpy.ndarray): The input data to be normalized.
        - isValid (bool): Whether the input data is from the validation dataset (default: False).

        Returns:
        - normalized_data (numpy.ndarray): The normalized input data.
        """
        if isValid:
            min_vals = self.train_min_values
            max_vals = self.train_max_values
        else:
            min_vals = np.min(X, axis=0)
            max_vals = np.max(X, axis=0)
            self.train_min_values = min_vals
            self.train_max_values = max_vals
        normalized_data = (X - min_vals) / (max_vals - min_vals)
        return normalized_data
    
    def train(self, X_train, X_valid):
        """
        Trains the anomaly detection neural network.

        Args:
        - X_train (numpy.ndarray): The training data.
        - X_valid (numpy.ndarray): The validation data.
        """
        # Normalize training and validation data
        normalized_training_data = self._normalize_data(X_train)
        normalized_validation_data = self._normalize_data(X_valid, True)
        # Convert data to PyTorch tensors
        train_dataset = TensorDataset(torch.tensor(normalized_training_data, dtype=torch.float32))
        train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
        valid_dataset = TensorDataset(torch.tensor(normalized_validation_data, dtype=torch.float32))
        valid_loader = DataLoader(valid_dataset, batch_size=64, shuffle=False)
        # Initialize model, optimizer, and loss function
        input_dim = normalized_training_data.shape[1]
        self.input_dim = input_dim
        self.model = AnomalyDetectionNN(self.input_dim, self.train_min_values, self.train_max_values)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        best_loss = float('inf')
        counter = 0
        for epoch in range(self.num_epochs):
            self.model.train()
            running_loss = 0.0
            for batch_inputs in train_loader:
                self.optimizer.zero_grad()
                for inputs in batch_inputs:  # Iterate over each tensor in the batch
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, inputs)  # Reconstruction loss (MSE)
                    loss.backward()
                    self.optimizer.step()
                    running_loss += loss.item() * inputs.size(0)
            # epoch_loss = running_loss / len(train_loader.dataset)
            # print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}") # traning loss
            # Evaluate validation loss
            with torch.no_grad():
                valid_loss = 0.0
                for valid_inputs in valid_loader:
                    for inputs in valid_inputs:
                        outputs = self.model(inputs)
                        loss = self.criterion(outputs, inputs)
                        valid_loss += loss.item() * inputs.size(0)
                valid_loss /= len(valid_loader.dataset)
            if valid_loss < best_loss:
                best_loss = valid_loss
                counter = 0
            else:
                counter += 1
            if counter >= self.patience:
                # print("Validation loss has not improved for {} epochs. Early stopping.".format(patience))
                break
    
    def predict(self, X, threshold = 0.0002):
        """
        Predicts anomalies in the input data.

        Args:
        - X (numpy.ndarray): The input data.
        - threshold (float): The threshold for anomaly detection (default: 0.0002).

        Returns:
        - predictions (torch.Tensor): Tensor containing the predictions (1 for anomaly, 0 for normal) for each input sample.
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        with torch.no_grad():
            normalized_data = self._normalize_data(X, True)
            X_tensor = torch.tensor(normalized_data, dtype=torch.float32)
            self.model.eval()
            reconstructed_data = self.model(X_tensor)
            reconstruction_loss = torch.mean(torch.square(X_tensor - reconstructed_data), dim=1)
            predictions = (reconstruction_loss > threshold).int()
        return predictions



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






        
    

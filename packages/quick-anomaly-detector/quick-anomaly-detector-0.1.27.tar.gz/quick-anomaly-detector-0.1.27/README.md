# AnomalyDetectionModel
AnomalyDetectionModels

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`AnomalyDetectionModel` is a python library that includs some simple implementation of an anomaly detection model.   
For more details, please refer to the document page:   
[Document](https://anomalydetectionmodel.readthedocs.io/en/latest/index.html)   
pypi page link is here:(https://pypi.org/project/quick-anomaly-detector/)   

### Quick Start
#### Installation

You can install `Anomaly DetectionModel` using pip:

```
pip install quick-anomaly-detector
```

Quick Start:   
```
from quick_anomaly_detector.models import AnomalyDetectionModel


# Load your datasets (X_train, X_val, y_val)
model = AnomalyDetectionModel()

# Train the model
model.train(X_train, X_val, y_val)

# Predict anomalies in the validation dataset
anomalies = model.predict(X_val)

```
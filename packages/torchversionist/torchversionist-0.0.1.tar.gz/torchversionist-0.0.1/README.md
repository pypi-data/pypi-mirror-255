# TorchVersionist

<p align="center">
  <img src="assets/logo.png" width="400" height="400" alt="TorchVersionist Logo">
</p>



TorchVersionist is a powerful Python library designed for PyTorch users to effortlessly manage model versions. It automates the tracking of model architectures, hyperparameters, and performance metrics, facilitating a smoother development and analysis process.

## Key Features

- **Automated Model Versioning**: Automatically assign and track versions for each of your PyTorch models.
- **Detailed Metadata Tracking**: Store and retrieve comprehensive metadata and hyperparameters for each model iteration.
- **Performance Metrics Logging**: Keep a record of model performance metrics for easy comparison and analysis.
- **Intuitive Model Retrieval**: Quickly access any version of your model with straightforward retrieval functions.

## Installation

```bash
pip install TorchVersionist
```

## Usage
Here's a quick start on how to use TorchVersionist:
```python
from torchversionist import ModelManager
# Initialize with your PyTorch model
model_manager = ModelManager(your_model, model_name="example_model")

# After training your model
model_manager.save(meta_data={'training_details': '...'}, metrics={'accuracy': 0.95})
```


## Contributing
Contributions to TorchVersionist are welcome! Open an issue or submit pull requests for any improvements or bug fixes.


## License
Licensed under the MIT License. 

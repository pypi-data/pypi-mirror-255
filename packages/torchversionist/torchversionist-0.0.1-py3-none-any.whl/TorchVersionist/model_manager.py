import os
import json
import torch
from training_metric import TrainingMetric
from training_metric_tracker import TrainingMetricsTracker



class ModelManager:
    def __init__(self, model, model_name, base_dir="models"):
        self.model = model
        self.model_name = model_name
        
        # Define separate subdirectories for models and metadata
        self.model_dir = os.path.join(base_dir, model_name, "models")
        self.metadata_dir = os.path.join(base_dir, model_name, "meta_data")
        
        # Create directories if they don't exist
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)

        self.metadata = self.extract_model_info(model)
        self.metrics = {}
        self.training_metrics_tracker = TrainingMetricsTracker()  # Initialize the metrics tracker

    
    def extract_model_info(self, model):
        model_info = {}

        # Iterate over all modules and layers
        for name, module in model.named_children():
            layer_info = {
                'layer_type': str(module.__class__.__name__),
                # Initialize as None and fill in if possible
                'in_features': None,
                'out_features': None,
                'out_channels': None,
                'kernel_size': None,
                # ... (other properties)
            }

            # Try to extract properties based on layer/module type
            if hasattr(module, 'in_features'):
                layer_info['in_features'] = module.in_features
                layer_info['out_features'] = module.out_features
            if hasattr(module, 'out_channels'):
                layer_info['out_channels'] = module.out_channels
                layer_info['kernel_size'] = module.kernel_size[0] if isinstance(module.kernel_size, tuple) else module.kernel_size
                layer_info['stride'] = module.stride
                layer_info['padding'] = module.padding
            # ... (other layer-specific properties)

            # Count trainable parameters for the layer/module
            layer_info['trainable_params'] = sum(p.numel() for p in module.parameters() if p.requires_grad)

            # Recursively get info from nested modules (e.g., nn.Sequential)
            if len(list(module.children())) > 0:
                layer_info['children'] = self.extract_model_info(module)

            model_info[name] = layer_info

        model_architecture = {"model_architecture": model_info}
        return model_architecture
    
    def assign_version(self):
        # Get the list of model files in the specific model's directory
        model_files = [f for f in os.listdir(self.model_dir) if f.endswith('.pt')]

        # Extract version numbers and find the latest version
        versions = [int(f.split('_')[1].split('.')[0]) for f in model_files]
        latest_version = max(versions) if versions else 0
        return latest_version + 1
        
    def save(self, meta_data=None, metrics=None):
        # If additional meta_data is provided, update the self.metadata dictionary
        if meta_data:
            self.metadata.update(meta_data)
    
        # If metrics are provided, update the self.metrics dictionary
        if metrics:
            self.metrics.update(metrics)
        
        # Assign a version number to the model
        version = self.assign_version()
        
        # Define the file paths for the model and metadata
        model_path = os.path.join(self.model_dir, f"model_{version}.pt")
        meta_path = os.path.join(self.metadata_dir, f"model_{version}_meta_data.json")
        
        # Save the PyTorch model state dictionary
        torch.save(self.model.state_dict(), model_path)
        
        # Prepare the data to be saved in the meta file
        save_data = {
            'meta_data': self.metadata,
            'metrics': self.metrics,
            'training_metrics': json.loads(self.training_metrics_tracker.to_json()) if self.training_metrics_tracker else None
        }
        
        # Save metadata in a _metadata.json file in JSON format
        with open(meta_path, 'w') as meta_file:
            json.dump(save_data, meta_file, indent=4)
        
        return version

    def load(self, version):
        model_path = os.path.join(self.model_dir, f"model_{version}.pt")
        meta_path = os.path.join(self.model_dir, f"model_{version}.meta")
        
        # Load PyTorch model
        self.model.load_state_dict(torch.load(model_path))
        
        # Load metadata and metrics
        with open(meta_path, 'r') as meta_file:
            data = json.load(meta_file)
            self.metadata = data['metadata']
            self.metrics = data['metrics']
        
        return self.model, self.metadata, self.metrics
    
    def update_metrics(self, new_metrics):
        """
        Update the metrics dictionary with new metrics.
        :param new_metrics: A dictionary containing new metrics to be added or updated.
        """
        # Update the self.metrics dictionary with the new metrics
        self.metrics.update(new_metrics)

    def add_training_metric(self, epoch, metric_name, value):
        """
        Add a training metric to the metrics tracker.
        :param epoch: The training epoch or iteration.
        :param metric_name: The name of the metric.
        :param value: The value of the metric.
        """
        training_metric = TrainingMetric(epoch, metric_name, value)
        self.training_metrics_tracker.add_training_metric(training_metric)
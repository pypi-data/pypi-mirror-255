import os
import json

from training_metric import TrainingMetric
from training_metric_tracker import TrainingMetricsTracker

class ModelLoader:
    def __init__(self, model_name, base_dir="models"):
        """
        Initialize the ModelLoader with a specific model name.
        :param model_name: The name of the model whose data is to be loaded.
        :param base_dir: Base directory where models and metadata are stored.
        """
        self.model_name = model_name
        self.metadata_dir = os.path.join(base_dir, model_name, "meta_data")

    def load_metric_data(self, metric_name):
        """
        Load data for a specific metric across different model versions.
        :param metric_name: The name of the metric to load data for.
        :return: Two lists - versions and corresponding metric values.
        """
        versions = []
        metric_values = []
        
        # Check if the metadata directory exists
        if not os.path.isdir(self.metadata_dir):
            raise FileNotFoundError(f"Metadata directory for model {self.model_name} not found, please check the model name.")

        # Scan the metadata directory and collect metric data
        for meta_file in sorted(os.listdir(self.metadata_dir)):
            if meta_file.endswith('_meta_data.json'):
                with open(os.path.join(self.metadata_dir, meta_file), 'r') as file:
                    metadata = json.load(file)
                    if metric_name in metadata['metrics']:
                        version = int(meta_file.split('_')[1])
                        versions.append(version)
                        metric_values.append(metadata['metrics'][metric_name])

        return versions, metric_values

    def load_training_metrics(self, version):
        """
        Load training metrics for a specific model version.
        :param version: The version number of the model.
        :return: An instance of TrainingMetricsTracker with loaded metrics.
        """
        meta_file = os.path.join(self.metadata_dir, f"model_{version}_meta_data.json")

        if not os.path.exists(meta_file):
            raise FileNotFoundError(f"No metadata found for model version {version}")

        with open(meta_file, 'r') as file:
            metadata = json.load(file)
            metrics_data = metadata.get('training_metrics', [])

        # Reconstruct the TrainingMetricsTracker from the metrics data
        metrics_tracker = TrainingMetricsTracker()
        for item in metrics_data:
            metrics_tracker.add_training_metric(TrainingMetric(item['epoch'], item['metric_name'], item['value']))

        return metrics_tracker
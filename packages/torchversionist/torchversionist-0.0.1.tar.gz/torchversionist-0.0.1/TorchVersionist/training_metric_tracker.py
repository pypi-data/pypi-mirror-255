import json
import matplotlib.pyplot as plt
from training_metric import TrainingMetric


class TrainingMetricsTracker:
    def __init__(self):
        """
        Initialize the training metrics tracker.
        """
        self.metric_snapshots = []

    def add_training_metric(self, training_metric):
        """
        Add a training metric to the collection of metric snapshots.
        :param snapshot: An instance of TrainingMetric.
        """
        self.metric_snapshots.append(training_metric)

    def to_json(self):
        """
        Serialize the entire collection of TraningMetric to a JSON string.
        :return: A JSON string representation of the TraningMetric.
        """
        return json.dumps([ms.__dict__ for ms in self.metric_snapshots])
    
    @staticmethod
    def from_json(json_data):
        """
        Create a TrainingMetricsTracker instance from JSON data.
        :param json_data: A JSON string representation of metric snapshots.
        :return: A TrainingMetricsTracker instance.
        """
        tracker = TrainingMetricsTracker()
        data = json.loads(json_data)

        for item in data:
            traning_metric = (item['epoch'], item['metric_name'], item['value'])
            tracker.add_training_metric(TrainingMetric(*traning_metric))
            
        return tracker


    def plot_metric(self, metric_name):
        """
        Create a plot of the progression of a specified metric over time and return the figure.
        :param metric_name: The name of the metric to plot.
        :return: A matplotlib figure object.
        """
        epochs = [snapshot.epoch for snapshot in self.metric_snapshots if snapshot.metric_name == metric_name]
        values = [snapshot.value for snapshot in self.metric_snapshots if snapshot.metric_name == metric_name]

        if not epochs:
            raise ValueError(f"No data found for metric '{metric_name}'")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(epochs, values, marker='o')
        ax.set_title(f"Progression of {metric_name}")
        ax.set_xlabel("Epoch")
        ax.set_ylabel(metric_name.capitalize())
        ax.grid(True)

        return fig
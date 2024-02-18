import matplotlib.pyplot as plt
import os
import json
from model_loader import ModelLoader
import warnings

class ModelAnalyzer:
    def __init__(self, model_name, base_dir="models"):
        """
        Initialize the ModelAnalyzer with a specific model name.
        :param model_name: The name of the model to analyze.
        :param base_dir: Base directory where models and metadata are stored.
        """
        self.model_name = model_name
        self.model_loader = ModelLoader(model_name, base_dir)

    def plot_metric(self, metric_name):
        """
        Create a plot of the progression of a specified metric over different model versions and return the figure.
        :param metric_name: The name of the metric to plot.
        :return: A matplotlib figure object.
        """
        versions, metric_values = self.model_loader.load_metric_data(metric_name)
        
        if len(metric_values) == 0:
            warnings.warn(f"No metric data found for metric {metric_name} and model {self.model_name}.")
        
        # Create a figure and plot the metric progression
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(versions, metric_values, marker='o')
        ax.set_title(f"Progression of {metric_name} over Model Versions")
        ax.set_xlabel("Model Version")
        ax.set_ylabel(metric_name)
        ax.grid(True)

        return fig 



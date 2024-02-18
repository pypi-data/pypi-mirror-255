import torch
import matplotlib.pyplot as plt

from model_manager import ModelManager
from model_analyzer import ModelAnalyzer
from model_loader import ModelLoader


# remove the model directory if it exists
import shutil
# shutil.rmtree("models", ignore_errors=True)

# # Create a PyTorch model
# model = torch.nn.Sequential(
#     torch.nn.Linear(10, 10),
#     torch.nn.ReLU(),
#     torch.nn.Linear(10, 1),
#     torch.nn.Sigmoid()
# )

# # Create a model manager object
# model_manager = ModelManager(model, "my_model")

# # add a metric to track
# model_manager.update_metrics({"accuracy": 0.1})

# model_manager.add_training_metric(0, "acc", 0)

# model_manager.add_training_metric(1, "acc", 0.1)

# model_manager.add_training_metric(2, "acc", 0.2)

# model_manager.add_training_metric(3, "acc", 0.3)

# model_manager.add_training_metric(4, "acc", 0.4)

# model_manager.save()

# load the model

model_loader = ModelLoader("my_model")

training_phase_metrics = model_loader.load_training_metrics(1)

# plot the metric
fig = training_phase_metrics.plot_metric("acc")
plt.show()




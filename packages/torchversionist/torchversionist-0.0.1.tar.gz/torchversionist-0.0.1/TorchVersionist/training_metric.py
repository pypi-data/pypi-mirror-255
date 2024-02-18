import json

class TrainingMetric:
    def __init__(self, epoch, metric_name, value):
        """
        Initialize a training metric.
        :param epoch: The training epoch or iteration.
        :param metric_name: The name of the metric.
        :param value: The value of the metric.
        """
        self.epoch = epoch
        self.metric_name = metric_name
        self.value = value

    def to_json(self):
        """
        Serialize the training metric to a JSON string.
        :return: A JSON string representation of the training metric.
        """
        return json.dumps(self.__dict__)

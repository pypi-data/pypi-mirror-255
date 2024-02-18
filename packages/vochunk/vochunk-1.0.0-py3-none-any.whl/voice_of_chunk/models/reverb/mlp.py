import torch
import torch.nn as nn
import torch.nn.functional as F


class ReverbClassifierNetwork(nn.Module):
    """
    VoiceNonVoiceClassifier

    Neural network architecture binary classifier.
    """

    def __init__(self):
        super(ReverbClassifierNetwork, self).__init__()
        self.fc0 = nn.Linear(128, 2048)
        self.fc1 = nn.Linear(2048, 512)
        self.fc2 = nn.Linear(512, 2)

    # x represents our data
    def forward(self, x):
        # Pass data through linear layer
        x = self.fc0(x)
        x = F.relu(x)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)

        # Apply softmax to x
        output = F.log_softmax(x, dim=1)
        return output

import torch.nn as nn

class NicheMLP(nn.Module):
    def __init__(self, in_features, out_features, hidden_features, n_layers):
        super().__init__()

        layers = []
        layers.append(nn.Linear(in_features, hidden_features))
        layers.append(nn.ReLU())
        for _ in range(n_layers - 1):
            layers.append(nn.Linear(hidden_features, hidden_features))
            layers.append(nn.ReLU())
        layers.append(nn.Linear(hidden_features, out_features))
        
        self.mlp = nn.Sequential(*layers)

    def forward(self, x):
        return self.mlp(x)
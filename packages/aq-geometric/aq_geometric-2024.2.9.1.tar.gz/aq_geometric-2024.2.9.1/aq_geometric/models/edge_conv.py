import torch
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Linear, ReLU
from torch_geometric.nn import MessagePassing


class EdgeConv(MessagePassing):
    def __init__(self, in_channels, out_channels):
        super().__init__(aggr='max')
        self.mlp = Seq(Linear(2 * in_channels, out_channels), ReLU(),
                       Linear(out_channels, out_channels))

    def forward(self, x, edge_index):
        # x has shape [N, in_channels]
        # edge_index has shape [2, E]

        return self.propagate(edge_index, x=x)

    def message(self, x_i, x_j):
        # x_i has shape [E, in_channels]
        # x_j has shape [E, in_channels]

        tmp = torch.cat([x_i, x_j - x_i],
                        dim=1)  # tmp has shape [E, 2 * in_channels]
        return self.mlp(tmp)


class EdgeConvModel(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = EdgeConv(in_channels, out_channels)
        self.conv2 = EdgeConv(out_channels, out_channels)
        self.conv3 = EdgeConv(out_channels, out_channels)
        self.max_pool = torch.nn.MaxPool1d(in_channels)
        self.fc = torch.nn.Linear(
            16, 1
        )  # shape of the input to the linear layer is 8 for 128 hidden units and 16 for 256?

    def forward(self, x, edge_index):
        x_1 = self.conv1(x, edge_index)
        x_2 = x_1.relu()
        x_3 = self.conv2(x_2, edge_index)
        x_4 = x_3.relu()
        x_5 = self.conv3(x_4, edge_index)
        x_6 = x_5.relu()
        # concatenate
        x_7 = torch.cat((x_2, x_4, x_6), dim=1)
        # max pool
        x_8 = self.max_pool(x_7)
        # linear
        x_9 = self.fc(x_8)
        return x_9

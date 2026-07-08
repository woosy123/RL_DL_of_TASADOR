import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class FullyConnectedNet(nn.Module):
    def __init__(self):
      super(FullyConnectedNet, self).__init__()
      self.fc1 = nn.Linear(13, 32)
      self.fc2 = nn.Linear(32, 8)

    def forward(self, x):
      x = self.fc1(x.float())
      x = F.relu(x)
      output = self.fc2(x)

      return output

class CasualConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, 
                 stride=1, dilation=1, groups=1, bias=True):
        super(CasualConv1d, self).__init__()
        self.dilation = dilation
        padding = dilation * (kernel_size - 1)
        self.conv1d = nn.Conv1d(in_channels, out_channels, kernel_size, stride,
                                padding, dilation, groups, bias)

    def forward(self, input):
        # Takes something of shape (N, in_channels, T),
        # returns (N, out_channels, T)
        out = self.conv1d(input)
        return out[:, :, :-self.dilation] # TODO: make this correct for different strides/padding

class DenseBlock(nn.Module):
    def __init__(self, in_channels, dilation, filters, kernel_size=2):
        super(DenseBlock, self).__init__()
        self.casualconv1 = CasualConv1d(in_channels, filters, kernel_size, dilation=dilation)
        self.casualconv2 = CasualConv1d(in_channels, filters, kernel_size, dilation=dilation)

    def forward(self, input):
        # input is dimensions (N, in_channels, T)
        xf = self.casualconv1(input)
        xg = self.casualconv2(input)
        activations = torch.tanh(xf) * torch.sigmoid(xg) # shape: (N, filters, T)
        return torch.cat((input, activations), dim=1)
        
class TCBlock(nn.Module):
    def __init__(self, in_channels, seq_length, filters):
        super(TCBlock, self).__init__()
        self.dense_blocks = nn.ModuleList([DenseBlock(in_channels + i * filters, 2 ** (i+1), filters)
                                           for i in range(int(math.ceil(math.log(seq_length, 2))))])

    def forward(self, input):
        # input is dimensions (N, T, in_channels)
        input = torch.transpose(input, 1, 2)
        for block in self.dense_blocks:
            input = block(input)
        return torch.transpose(input, 1, 2)

class AttentionBlock(nn.Module):
    def __init__(self, in_channels, key_size, value_size):
        super(AttentionBlock, self).__init__()
        self.linear_query = nn.Linear(in_channels, key_size)
        self.linear_keys = nn.Linear(in_channels, key_size)
        self.linear_values = nn.Linear(in_channels, value_size)
        self.sqrt_key_size = math.sqrt(key_size)

    def forward(self, input):
        # input: (N, T, in_channels)
        N, T, _ = input.shape

        mask = torch.triu(
            torch.ones((T, T), device=input.device, dtype=torch.bool),
            diagonal=1
        )

        keys = self.linear_keys(input)          # (N, T, key_size)
        query = self.linear_query(input)        # (N, T, key_size)
        values = self.linear_values(input)      # (N, T, value_size)

        temp = torch.bmm(query, keys.transpose(1, 2))  # (N, T, T)

        temp = temp.masked_fill(mask, -float('inf'))

        temp = F.softmax(temp / self.sqrt_key_size, dim=1)  # (N, T, T)
        temp = torch.bmm(temp, values)                      # (N, T, value_size)
        return torch.cat((input, temp), dim=2)              # (N, T, in_channels+value_size)
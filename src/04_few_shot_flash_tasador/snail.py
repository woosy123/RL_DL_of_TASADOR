import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from blocks import *
from params import *


class SnailFewShot(nn.Module):
    def __init__(self, N, K, task, use_cuda=False):
        # N-way (N classes, N = 1 for regression tasks), K-shot (K samples, default K = 1)
        super(SnailFewShot, self).__init__()
        if task == 'sizeless' or task == 'tasador' or task == 'multicloud' or task == 'openwhisk':
            self.encoder = FullyConnectedNet()
            # num_channels is the dimension of x which is equal to the number of features per shot/sample
            num_channels = NUM_FEATURES_PER_SHOT  # 8 (if self.encoder is applied to input)
        else:
            raise ValueError('Not recognized task!')

        num_filters = int(math.ceil(math.log(N * K + 1, 2)))
        self.attention1 = AttentionBlock(num_channels, 64, 32)
        num_channels += 32
        self.tc1 = TCBlock(num_channels, N * K + 1, 128)
        num_channels += num_filters * 128
        self.attention2 = AttentionBlock(num_channels, 256, 128)
        num_channels += 128
        self.tc2 = TCBlock(num_channels, N * K + 1, 128)
        num_channels += num_filters * 128
        self.attention3 = AttentionBlock(num_channels, 512, 256)
        num_channels += 256

        self.fc = nn.Linear(num_channels, N)
        if FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT:
            self.fc1 = nn.Linear(num_channels * K + NUM_FEATURES_PER_SHOT * K + NUM_CONFIG_PARAMS, 256)
        else:
            self.fc1 = nn.Linear(num_channels * K + NUM_CONFIG_PARAMS, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, N)
        self.relu = nn.ReLU()

        self.N = N
        self.K = K
        self.use_cuda = use_cuda

    # embedding + fully-connected layer
    def forward(self, input, labels):
        # x = self.encoder(input)
        # input to the embedding layer is the features to the samples (excluding the config to predict for)
        x = input[:, :NUM_FEATURES_PER_SHOT * self.K]
        batch_size = input.size(0)
        x = x.view(batch_size, self.K, NUM_FEATURES_PER_SHOT).float()   

        # apply the embedding layer
        x = self.attention1(x.float())
        x = self.tc1(x)
        x = self.attention2(x)
        x = self.tc2(x)
        x = self.attention3(x)
        # add a fully connected layer before passing the embedding
        # x = self.fc(x)

        if FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT:
            x = x.view(batch_size, 1, -1)
            input2 = input.view(batch_size, 1, -1)
            x = torch.cat((x, input2), 2)
        else:
            x = x.view(batch_size, 1, -1)
            config = input[:, -NUM_CONFIG_PARAMS:].view(batch_size, 1, NUM_CONFIG_PARAMS)
            x = torch.cat((x, config), 2)

        # go through a fully connected neural network
        x = self.relu(self.fc1(x.float()))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class SnailFewShotOnSizeless(nn.Module):
    def __init__(self, N, K, task, use_cuda=False):
        super(SnailFewShotOnSizeless, self).__init__()
        if task == 'sizeless' or task == 'tasador' or task == 'multicloud' or task == 'openwhisk':
            # num_channels is the dimension of x which is equal to the number of features per shot/sample
            num_channels = NUM_FEATURES_PER_SHOT
        else:
            raise ValueError('Not recognized task!')

        num_filters = int(math.ceil(math.log(N * K + 1, 2)))
        self.attention1 = AttentionBlock(num_channels, 64, 32)
        num_channels += 32
        self.tc1 = TCBlock(num_channels, N * K + 1, 128)
        num_channels += num_filters * 128
        self.attention2 = AttentionBlock(num_channels, 256, 128)
        num_channels += 128
        self.tc2 = TCBlock(num_channels, N * K + 1, 128)
        num_channels += num_filters * 128
        self.attention3 = AttentionBlock(num_channels, 512, 256)
        num_channels += 256

        if FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT:
            self.fc1 = nn.Linear(num_channels * K + NUM_FEATURES_PER_SHOT * K + NUM_CONFIG_PARAMS, 256)
        else:
            self.fc1 = nn.Linear(num_channels * K + NUM_CONFIG_PARAMS, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 256)
        self.fc4 = nn.Linear(256, 256)
        self.fc5 = nn.Linear(256, N)
        self.relu = nn.ReLU()

        self.N = N
        self.K = K
        self.use_cuda = use_cuda

    # embedding + fully-connected layer (Sizeless architecture)
    def forward(self, input, labels):
        # input to the embedding layer is the features to the samples (excluding the config to predict for)
        x = input[:, :NUM_FEATURES_PER_SHOT * self.K]
        x = x.view(batch_size, self.K, NUM_FEATURES_PER_SHOT).float()

        # apply the embedding layer
        x = self.attention1(x.float())
        x = self.tc1(x)
        x = self.attention2(x)
        x = self.tc2(x)
        x = self.attention3(x)

 
        if FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT:
            x = x.view(batch_size, 1, -1)
            input2 = input.view(batch_size, 1, -1)
            x = torch.cat((x, input2), 2)
        else:
            x = x.view(batch_size, 1, -1)
            config = input[:, -NUM_CONFIG_PARAMS:].view(batch_size, 1, NUM_CONFIG_PARAMS)
            x = torch.cat((x, config), 2)

        # go through a fully connected neural network (Sizeless architecture)
        x = self.relu(self.fc1(x.float()))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.relu(self.fc4(x))
        x = self.fc5(x)
        return x

class Sizeless(nn.Module):
    def __init__(self, num_features=NUM_FEATURES_PER_SHOT + 1):
        super(Sizeless, self).__init__()
        self.fc1 = nn.Linear(num_features, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 256)
        self.fc4 = nn.Linear(256, 256)
        self.fc5 = nn.Linear(256, 1)
        self.relu = nn.ReLU()

    # fully-connected layers
    def forward(self, input, labels):
        input = input.view((1, 1, -1))
        x = self.relu(self.fc1(input.float()))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.relu(self.fc4(x))
        x = self.fc5(x)
        return x


class RNNFewShot(nn.Module):
    def __init__(self, N, K, task, use_cuda=False):
        # N-way (N classes, N = 1 for regression tasks), K-shot (K samples, default K = 1)
        super(RNNFewShot, self).__init__()
        
        if task == 'sizeless' or task == 'tasador' or task == 'multicloud' or task == 'openwhisk':
            self.encoder = FullyConnectedNet()
            # num_channels is the dimension of x which is equal to the number of features per shot/sample
            num_channels = NUM_FEATURES_PER_SHOT  # 8 (if self.encoder is applied to input)
        else:
            raise ValueError('Not recognized task!')

        self.hidden_size = 256
        self.num_layers = 2     # stack 2 RNN layers
        self.bidirectional = True
        self.directions = 2 if self.bidirectional else 1     # use bi-directional RNNs
        self.gru = nn.GRU(num_channels, self.hidden_size, num_layers=self.num_layers, batch_first=True, bidirectional=self.bidirectional)


        if FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT:
            self.fc1 = nn.Linear(self.directions * self.num_layers * self.hidden_size + NUM_FEATURES_PER_SHOT * K + NUM_CONFIG_PARAMS, 256)
        else:
            self.fc1 = nn.Linear(self.directions * self.num_layers * self.hidden_size + NUM_CONFIG_PARAMS, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, N)
        self.relu = nn.ReLU()

        self.N = N
        self.K = K
        self.use_cuda = use_cuda


    # embedding + fully-connected layer
    def forward(self, input, labels):
        batch_size = input.size(0)
        x = input[:, :NUM_FEATURES_PER_SHOT * self.K].float()
        x = x.view(batch_size, self.K, NUM_FEATURES_PER_SHOT)

        hidden = self.init_hidden()
        if self.use_cuda and input.is_cuda:
            hidden = hidden.to(input.device)

        output, h = self.gru(x, hidden)   # h: (directions*num_layers, batch, hidden_size)
        emb = h.transpose(0, 1).contiguous().view(batch_size, 1, -1)  # (batch, 1, directions*num_layers*hidden)

        if FEED_BOTH_SAMPLE_FEATURES_AND_CONFIGS_TO_PREDICT:
            inp = input.view(batch_size, 1, -1)
            z = torch.cat((emb, inp), dim=2)
        else:
            config = input[:, -NUM_CONFIG_PARAMS:].view(batch_size, 1, NUM_CONFIG_PARAMS).float()
            z = torch.cat((emb, config), dim=2)

        z = self.relu(self.fc1(z))
        z = self.relu(self.fc2(z))
        z = self.fc3(z)
        return z


    def init_hidden(self):
        return torch.zeros((self.directions * self.num_layers, 1, self.hidden_size))
    
    
    def get_embedding(self, input):
        """

        """
        batch_size = input.size(0)
        x = input[:, :NUM_FEATURES_PER_SHOT * self.K].float()
        x = x.view(batch_size, self.K, NUM_FEATURES_PER_SHOT)

        hidden = self.init_hidden()
        if self.use_cuda and input.is_cuda:
            hidden = hidden.to(input.device)

        output, h = self.gru(x, hidden)
        emb = h.transpose(0, 1).contiguous().view(batch_size, -1)
        return emb

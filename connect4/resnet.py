import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from Connect4Node import Connect4Node
from MCTS import MCTS

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

# Define a basic ResNet architecture
class ResNet(nn.Module):
    def __init__(self, num_blocks):
        super(ResNet, self).__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.layer1 = self._make_layer(64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(512, num_blocks[3], stride=2)
        self.fc = nn.Linear(512, 1)

    def _make_layer(self, out_channels, num_blocks, stride):
        strides = [stride] + [1]*(num_blocks-1)
        layers = []
        for stride in strides:
            layers.append(ResidualBlock(self.in_channels, out_channels, stride))
            self.in_channels = out_channels
        return nn.Sequential(*layers)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, out.size()[3])
        out = out.view(out.size(0), -1)
        out = self.fc(out)
        return out

# Create the ResNet model with the specified number of blocks in each layer
# model = ResNet(num_blocks=[2, 2, 2, 2])
# print(model)

class Connect4ResNet(nn.Module):
    def __init__(self, block, layers):
        super(Connect4ResNet, self).__init__()

        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)

        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 64, layers[1], stride=2)

        self.fc_policy = nn.Linear(64 * 6 * 7, 7)  # Assuming you flatten the tensor and have 7 possible moves for Connect Four
        self.fc_value = nn.Linear(64 * 6 * 7, 1)

    def _make_layer(self, block, out_channels, blocks, stride=1):
        layers = []
        layers.append(block(64, out_channels, stride))
        for _ in range(1, blocks):
            layers.append(block(out_channels, out_channels))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))

        x = self.layer1(x)
        x = self.layer2(x)

        x = x.view(x.size(0), -1)  # Flatten the tensor

        policy = self.fc_policy(x)
        value = torch.tanh(self.fc_value(x))

        return policy, value



class Connect4ResNetTrainer:
    def __init__(self, model):
        self.model = model
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion_policy = nn.CrossEntropyLoss()
        self.criterion_value = nn.MSELoss()

    def create_board(self):
        return np.zeros((6, 7), int)

    def generate_data(self, num_games):
        data_list = []
        for _ in range(num_games):
            game_history = []
            board = self.create_board()
            node = Connect4Node(board)

            while not node.is_terminal():
                new_node = node.find_random_child()
                game_history.append((new_node.board, new_node.last_move))
                node = new_node
            winner = node.player
            for state, action in game_history:
                data = (state, action, winner)
                print(data)
                data_list.append(data)
        return data_list


    def int_to_board(self, board_int):
        rows, cols = 6, 7
        board = np.zeros((rows, cols), dtype=np.int8)
        mask = 0b11  # Mask to extract 2 bits

        for row in range(rows):
            for col in range(cols):
                # Calculate the position of the bits in the integer
                pos = 2 * (row * cols + col)
                # Extract the bits for the current cell and assign it to the board
                board[row, col] = (board_int >> pos) & mask

        return board

    def train_resnet(self, data, epochs=5):
        for epoch in range(epochs):
            for state, action, winner in data:
                self.optimizer.zero_grad()
                board = self.int_to_board(state)
                # Convert board state to PyTorch tensor and add a batch and channel dimension
                board_tensor = torch.FloatTensor(board).unsqueeze(0).unsqueeze(0)
                
                # Forward pass
                policy, value = self.model(board_tensor)
                
                # Convert action and winner to PyTorch tensors
                action_tensor = torch.LongTensor([action])
                winner_tensor = torch.FloatTensor([winner])
                
                # Compute the loss
                loss_policy = self.criterion_policy(policy, action_tensor)
                loss_value = self.criterion_value(value, winner_tensor)
                loss = loss_policy + loss_value
                
                # Backward pass and optimization
                loss.backward()
                self.optimizer.step()
                
    def self_play_train(self, iterations=1, num_games=1, epochs=1):
        for _ in range(iterations):
            data = self.generate_data(num_games)
            self.train_resnet(data, epochs)


# Usage example
resnet_model = Connect4ResNet(ResidualBlock, [2, 2])  # You need to define the ResBlock and adjust the layers accordingly
trainer = Connect4ResNetTrainer(resnet_model)
trainer.self_play_train()

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

class TabularMLP(nn.Module):
    def __init__(self, input_features, output_features, layers, task_type='regression', device='cpu'):
        super(TabularMLP, self).__init__()
        self.device = device
        self.task_type = task_type

        # Build the MLP layers
        all_layers = []
        for i in range(len(layers)):
            input_dim = input_features if i == 0 else layers[i - 1]
            output_dim = layers[i]
            all_layers.append(nn.Linear(input_dim, output_dim))
            all_layers.append(nn.ReLU())  # Using ReLU as the activation function

        # Output layer
        if task_type == 'classification':
            all_layers.append(nn.Linear(layers[-1], output_features))
            all_layers.append(nn.Sigmoid())# if output_features == 1 else nn.Softmax(dim=1))
        else:  # Default to regression
            all_layers.append(nn.Linear(layers[-1], output_features))

        # Combine all layers
        self.layers = nn.Sequential(*all_layers)
        self.to(device)    
    
    def forward(self, x):
        return self.layers(x)


    def fit(self, X, y, n_iter=1000, learning_rate=0.01, batch_size=32, X_test=None, y_test=None):
        self.train()  # Set the model to training mode
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.MSELoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)

        # Initialize loss history
        self.train_loss_history = []
        self.test_loss_history = []

        # Check if test data is provided
        test_data_provided = X_test is not None and y_test is not None
        if test_data_provided:
            X_test, y_test = torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32)
            test_dataset = TensorDataset(X_test, y_test)
            test_dataloader = DataLoader(test_dataset, batch_size=batch_size)

        for epoch in range(n_iter):
            # Training loop
            train_loss_accum = 0.0
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)

                optimizer.zero_grad()
                outputs = self.forward(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                train_loss_accum += loss.item()

            # Average training loss for this epoch
            avg_train_loss = train_loss_accum / len(dataloader)
            self.train_loss_history.append(avg_train_loss)

            if test_data_provided:
                # Evaluation loop (test data)
                self.eval()  # Set the model to evaluation mode
                test_loss_accum = 0.0
                with torch.no_grad():
                    for X_batch, y_batch in test_dataloader:
                        X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                        outputs = self.forward(X_batch)
                        loss = criterion(outputs, y_batch)
                        test_loss_accum += loss.item()

                # Average test loss for this epoch
                avg_test_loss = test_loss_accum / len(test_dataloader)
                self.test_loss_history.append(avg_test_loss)

                self.train()  # Set the model back to training mode


    def predict(self, X):
        self.eval()  # Set the model to evaluation mode
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)
        with torch.no_grad():
            predictions = self.forward(X)
        return predictions.cpu().detach().numpy()
    
    def predict_proba(self, X):
        """Predict class probabilities for X."""
        if self.task_type != 'classification':
            raise ValueError("predict_proba is available only for classification tasks")

        self.eval()  # Set the model to evaluation mode
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)

        with torch.no_grad():
            outputs = self.forward(X)

        if self.layers[-1].__class__ == nn.Sigmoid:
            # For binary classification, return the sigmoid output directly
            return outputs.cpu().numpy()
        else:
            # For multi-class classification, return softmax probabilities
            probabilities = nn.functional.softmax(outputs, dim=1)
            return probabilities.cpu().numpy()

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import ast
# import safe_eval

class TorchEvalTabularMLP(nn.Module):
    def __init__(self, layers, device='cpu'):
        super(TorchEvalTabularMLP, self).__init__()
        # super(TabularMLP, self).__init__()
        self.device = device
        # self.task_type = task_type

        # Combine all layers
        self.layers = nn.Sequential(*layers)
        self.to(device)
    
    def forward(self, x):
        return self.layers(x)


    def fit(self, X, y, n_iter=1000, learning_rate=0.01, batch_size=32, X_test=None, y_test=None):
        self.train()  # Set the model to training mode
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.MSELoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)

        # Initialize loss history
        self.train_loss_history = []
        self.test_loss_history = []

        # Check if test data is provided
        test_data_provided = X_test is not None and y_test is not None
        if test_data_provided:
            X_test, y_test = torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32)
            test_dataset = TensorDataset(X_test, y_test)
            test_dataloader = DataLoader(test_dataset, batch_size=batch_size)

        for epoch in range(n_iter):
            # Training loop
            train_loss_accum = 0.0
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)

                optimizer.zero_grad()
                outputs = self.forward(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                train_loss_accum += loss.item()

            # Average training loss for this epoch
            avg_train_loss = train_loss_accum / len(dataloader)
            self.train_loss_history.append(avg_train_loss)

            if test_data_provided:
                # Evaluation loop (test data)
                self.eval()  # Set the model to evaluation mode
                test_loss_accum = 0.0
                with torch.no_grad():
                    for X_batch, y_batch in test_dataloader:
                        X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                        outputs = self.forward(X_batch)
                        loss = criterion(outputs, y_batch)
                        test_loss_accum += loss.item()

                # Average test loss for this epoch
                avg_test_loss = test_loss_accum / len(test_dataloader)
                self.test_loss_history.append(avg_test_loss)

                self.train()  # Set the model back to training mode


    def predict(self, X):
        self.eval()  # Set the model to evaluation mode
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)
        with torch.no_grad():
            predictions = self.forward(X)
        return predictions.cpu().detach().numpy()
    
    def predict_proba(self, X):
        """Predict class probabilities for X."""
        if self.task_type != 'classification':
            raise ValueError("predict_proba is available only for classification tasks")

        self.eval()  # Set the model to evaluation mode
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)

        with torch.no_grad():
            outputs = self.forward(X)

        if self.layers[-1].__class__ == nn.Sigmoid:
            # For binary classification, return the sigmoid output directly
            return outputs.cpu().numpy()
        else:
            # For multi-class classification, return softmax probabilities
            probabilities = nn.functional.softmax(outputs, dim=1)
            return probabilities.cpu().numpy()
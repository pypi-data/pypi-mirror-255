import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.utils.data import DataLoader, TensorDataset

import torch
from torch.utils.data import DataLoader, TensorDataset

class TorchLinearRegression:
    def __init__(self, fit_intercept=True, n_iter=1000, learning_rate=0.01, device='cpu'):
        self.fit_intercept = fit_intercept
        self.n_iter = n_iter
        self.learning_rate = learning_rate
        self.device = device

    def fit(self, X, y, batch_size=32):
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Adding bias term in weights for intercept
        n_features = X.shape[1] + 1 if self.fit_intercept else X.shape[1]
        self.weights = torch.zeros(n_features, device=self.device, requires_grad=True)

        for _ in range(self.n_iter):
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                if self.fit_intercept:
                    ones = torch.ones(X_batch.shape[0], 1, device=self.device)
                    X_batch = torch.cat((ones, X_batch), 1)

                y_pred = torch.matmul(X_batch, self.weights)
                loss = torch.mean((y_pred - y_batch) ** 2)
                loss.backward()

                with torch.no_grad():
                    self.weights -= self.learning_rate * self.weights.grad
                    self.weights.grad.zero_()

        if self.fit_intercept:
            self.intercept_ = self.weights[0].item()
            self.coef_ = self.weights[1:].cpu().detach().numpy()
        else:
            self.intercept_ = 0.0
            self.coef_ = self.weights.cpu().detach().numpy()

    def predict(self, X):
        X = torch.tensor(X, dtype=torch.float32)
        if self.fit_intercept:
            ones = torch.ones(X.shape[0], 1, device=self.device)
            X = torch.cat((ones, X.to(self.device)), 1)

        y_pred = torch.matmul(X, self.weights).cpu()
        return y_pred.detach().numpy()



class TorchElasticNet:
    def __init__(self, alpha=1.0, l1_ratio=0.5, n_iter=1000, learning_rate=0.01, fit_intercept=True, device='cpu'):
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.n_iter = n_iter
        self.learning_rate = learning_rate
        self.fit_intercept = fit_intercept
        self.device = device

    def fit(self, X, y, batch_size=32):
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        n_features = X.shape[1] + 1 if self.fit_intercept else X.shape[1]
        self.weights = torch.zeros(n_features, device=self.device, requires_grad=True)

        for _ in range(self.n_iter):
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
                if self.fit_intercept:
                    ones = torch.ones(X_batch.shape[0], 1, device=self.device)
                    X_batch = torch.cat((ones, X_batch), 1)

                predictions = torch.matmul(X_batch, self.weights)
                residuals = predictions - y_batch
                loss = torch.mean(residuals ** 2)
                
                l1_penalty = self.l1_ratio * torch.sum(torch.abs(self.weights))
                l2_penalty = (1 - self.l1_ratio) * torch.sum(self.weights ** 2)
                loss += self.alpha * (l1_penalty + l2_penalty)

                loss.backward()
                with torch.no_grad():
                    self.weights -= self.learning_rate * self.weights.grad
                    self.weights.grad.zero_()

        if self.fit_intercept:
            self.intercept_ = self.weights[0].item()
            self.coef_ = self.weights[1:].cpu().detach().numpy()
        else:
            self.intercept_ = 0.0
            self.coef_ = self.weights.cpu().detach().numpy()
    def predict(self, X):
        X = torch.tensor(X, dtype=torch.float32)
        if self.fit_intercept:
            ones = torch.ones(X.shape[0], 1, device=self.device)
            X = torch.cat((ones, X.to(self.device)), 1)

        predictions = torch.matmul(X, self.weights).cpu()
        return predictions.detach().numpy()



import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

class TorchSGDClassifier:
    def __init__(self, n_iter=1000, learning_rate=0.01, fit_intercept=True, device='cpu'):
        self.n_iter = n_iter
        self.learning_rate = learning_rate
        self.fit_intercept = fit_intercept
        self.device = device

    def fit(self, X, y, batch_size=32):
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        n_features = X.shape[1] + 1 if self.fit_intercept else X.shape[1]
        n_classes = len(torch.unique(y))

        # Simple linear model with softmax for classification
        self.model = nn.Linear(n_features, n_classes).to(self.device)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.model.parameters(), lr=self.learning_rate)

        for _ in range(self.n_iter):
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)

                if self.fit_intercept:
                    ones = torch.ones(X_batch.shape[0], 1, device=self.device)
                    X_batch = torch.cat((ones, X_batch), 1)

                optimizer.zero_grad()
                outputs = self.model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

        self.coef_ = self.model.weight.cpu().detach().numpy()
        self.intercept_ = self.model.bias.cpu().detach().numpy()

    def predict(self, X):
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)
        if self.fit_intercept:
            ones = torch.ones(X.shape[0], 1, device=self.device)
            X = torch.cat((ones, X), 1)

        
        outputs = self.model(X)
        _, predicted = torch.max(outputs.data, 1)
        return predicted.cpu().numpy()




import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

class TorchLinearRegressionNN(nn.Module):
    def __init__(self, device='cpu', fit_intercept = True):
        super(TorchLinearRegressionNN, self).__init__()
        self.linear = None  # Initialize linear layer later
        self.device = device
        self.fit_intercept = fit_intercept
        # Initialize attributes for coefficients and intercept
        self.coef_ = None
        self.intercept_ = None

    def forward(self, x):
        return self.linear(x)

    def fit(self, X, y, n_iter=1000, learning_rate=0.01, batch_size=32):
        # Detect number of features
        n_features = X.shape[1]

        # Initialize linear layer now that we know n_features
        self.linear = nn.Linear(n_features, 1).to(self.device)

        self.train()  # Set the model to training mode
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32).view(-1, 1)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.MSELoss()  # Mean Squared Error Loss
        optimizer = torch.optim.SGD(self.linear.parameters(), lr=learning_rate)

        for _ in range(n_iter):
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)

                optimizer.zero_grad()
                outputs = self.forward(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

        # Store the coefficients and intercept after training
        with torch.no_grad():
            self.coef_ = self.linear.weight.data.cpu().numpy().flatten()
            self.intercept_ = self.linear.bias.data.cpu().numpy().item()

    def predict(self, X):
        self.eval()  # Set the model to evaluation mode
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)
        with torch.no_grad():
            predictions = self.forward(X)
        return predictions.cpu().detach().numpy().flatten()




import torch

class TorchMatrixBasedLinearRegression:
    def __init__(self, fit_intercept=True, device='cpu'):
        self.fit_intercept = fit_intercept
        self.device = device
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
        X, y = X.to(self.device), y.to(self.device)

        if self.fit_intercept:
            ones = torch.ones(X.shape[0], 1, device=self.device)
            X = torch.cat((ones, X), 1)

        # Solving the normal equation
        X_transpose = torch.transpose(X, 0, 1)
        beta = torch.matmul(torch.matmul(torch.linalg.pinv(torch.matmul(X_transpose, X)), X_transpose), y)

        if self.fit_intercept:
            self.intercept_ = beta[0].item()
            self.coef_ = beta[1:].cpu().detach().numpy()
        else:
            self.intercept_ = 0.0
            self.coef_ = beta.cpu().detach().numpy()

    def predict(self, X):
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)

        if self.fit_intercept:
            # Add a column of ones to X for the intercept
            ones = torch.ones(X.shape[0], 1, device=self.device)
            X = torch.cat((ones, X), 1)

            # Combine intercept with coefficients
            intercept_tensor = torch.tensor([self.intercept_], device=self.device)
            coef_tensor = torch.tensor(self.coef_, device=self.device).flatten()
            combined_coef = torch.cat((intercept_tensor, coef_tensor))
        else:
            # Use coefficients only
            combined_coef = torch.tensor(self.coef_, device=self.device).flatten()

        predictions = torch.matmul(X, combined_coef)
        return predictions.cpu().detach().numpy()


import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

class LogisticRegressionNN(nn.Module):
    def __init__(self, n_features, device='cpu'):
        super(LogisticRegressionNN, self).__init__()
        self.linear = nn.Linear(n_features, 1)
        self.sigmoid = nn.Sigmoid()
        self.device = device
        self.to(device)

        # Initialize attributes for coefficients and intercept
        self.coef_ = None
        self.intercept_ = None

    def forward(self, x):
        x = self.linear(x)
        x = self.sigmoid(x)
        return x

    def fit(self, X, y, n_iter=1000, learning_rate=0.01, batch_size=32):
        self.train()
        X, y = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32).view(-1, 1)
        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        criterion = nn.BCELoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=learning_rate)

        for _ in range(n_iter):
            for X_batch, y_batch in dataloader:
                X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)

                optimizer.zero_grad()
                outputs = self.forward(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

        # Store the coefficients and intercept after training
        with torch.no_grad():
            self.coef_ = self.linear.weight.data.cpu().numpy().flatten()
            self.intercept_ = self.linear.bias.data.cpu().numpy().item()

    def predict(self, X):
        self.eval()
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)
        with torch.no_grad():
            outputs = self.forward(X)
        predictions = (outputs.cpu().numpy() > 0.5).astype(int)
        return predictions
    
    def predict_proba(self, X):
        self.eval()
        X = torch.tensor(X, dtype=torch.float32)
        X = X.to(self.device)
        with torch.no_grad():
            outputs = self.forward(X)
        predictions = (outputs.cpu().numpy()).astype(float)
        return predictions
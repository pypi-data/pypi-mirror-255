import torch

class KNNRegressor:
    def __init__(self, k=5, radius=float('inf'), device='cuda'):
        self.k = k
        self.radius = radius
        self.device = device
        self.data = None
        self.targets = None

    def fit(self, X, y):
        self.data = torch.tensor(X, dtype=torch.float32).to(self.device)
        self.targets = torch.tensor(y, dtype=torch.float32).to(self.device)

    def predict(self, X):
        query = torch.tensor(X, dtype=torch.float32).to(self.device)

        # Compute pairwise distances
        dists = torch.cdist(self.data, query)

        # Apply radius constraint
        within_radius = dists <= self.radius

        predictions = torch.zeros(query.shape[0], dtype=torch.float32)

        for i in range(query.shape[0]):
            valid_dists = dists[:, i][within_radius[:, i]]
            valid_targets = self.targets[within_radius[:, i]]

            # Ensure k is not greater than the number of valid points
            k = min(self.k, valid_dists.shape[0])

            if k > 0:
                # Get indices of 'k' nearest neighbors
                _, idx = torch.topk(valid_dists, k=k, largest=False)

                # Calculate the mean of the target values of the nearest neighbors
                predictions[i] = valid_targets[idx].mean()

        return predictions.cpu().numpy()

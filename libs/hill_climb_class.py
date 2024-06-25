import pandas as pd
import numpy as np


class HillClimb(object):
    """
        Class used to apply the
        algorithm Hill Climb
    """
    def __init__(self, data: pd.DataFrame) -> None:
        self.df = data

    def set_dataframe(self, data: dict or None=None) -> None:  # type: ignore
        if data:
            self.data = data
        self.df = pd.DataFrame(self.data)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)
        print(self.df)

    def initialize_weights(self, num_stocks: int) -> float:
        weights = np.random.rand(num_stocks)
        weights /= weights.sum()
        return weights

    def calculate_portfolio_return(self, weights: int) -> float:
        returns = self.df.pct_change().dropna()
        portfolio_return = np.dot(returns.mean(), weights)
        return portfolio_return

    def get_neighbor(self, weights: float) -> float:
        neighbor = weights.copy()
        idx = np.random.randint(len(weights))
        neighbor[idx] += np.random.uniform(-0.05, 0.05)
        neighbor = np.clip(neighbor, 0, 1)
        neighbor /= neighbor.sum()
        return neighbor

    def run(self, iterations: int =1000):
        num_stocks = self.df.shape[1]
        weights = self.initialize_weights(num_stocks)

        best_weights = weights
        best_return = self.calculate_portfolio_return(best_weights)

        for _ in range(iterations):
            neighbor = self.get_neighbor(best_weights)
            neighbor_return = self.calculate_portfolio_return(neighbor)
            if neighbor_return > best_return:
                best_weights = neighbor
                best_return = neighbor_return

        return best_weights, best_return


# object_ = HillClimb()
# object_.set_dataframe(object_.data)
# object_.run()

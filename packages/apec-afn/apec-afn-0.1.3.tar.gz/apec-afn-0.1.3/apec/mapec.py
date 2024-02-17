import torch
import torch.nn as nn


class MAPEC(nn.Module):
    """
    MAPEC (Multiplicative Asymmetric Parametric Exponential Curvature) activation function.
    """

    def __init__(
        self,
        num_features: int = 1,
        alpha: float = -3.333e-2,
        beta: float = -0.1,
        gamma: float = -2.0,
        delta: float = +0.1,
        zeta: float = +1.0,
        eps: float = 1.0e-3,
    ) -> None:
        super(MAPEC, self).__init__()

        self.eps = eps

        alphas = [alpha] * num_features
        betas = [beta] * num_features
        gammas = [gamma] * num_features
        deltas = [delta] * num_features
        zetas = [zeta] * num_features

        coefficients = torch.tensor([alphas, betas, gammas, deltas, zetas])
        coefficients = torch.nn.Parameter(coefficients)
        self.register_parameter("coefficients", coefficients)

        pass

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        a = self.coefficients[0]
        b = self.coefficients[1]
        g = self.coefficients[2]
        d = self.coefficients[3]
        z = self.coefficients[4]
        x = (a + (b - x) / (-g.abs() - torch.exp(-x) - self.eps) + (x * d)) * z
        return x

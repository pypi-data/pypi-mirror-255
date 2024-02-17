import torch
import torch.nn as nn


class MAPEC(nn.Module):
    """
    MAPEC (Multiplicative Asymmetric Parametric Exponential Curvature) activation function.
    """

    def __init__(
        self,
        eps: float = 1.0e-3,
    ) -> None:
        super(MAPEC, self).__init__()

        self.eps = eps

        coefficients = torch.tensor([+0.0, +0.0, -1.0, +0.0])
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
        x = a + (b - x) / (-g.abs() - torch.exp(-x) - self.eps) + (x * d)
        return x

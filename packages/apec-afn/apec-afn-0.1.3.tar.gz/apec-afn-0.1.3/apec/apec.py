import torch
import torch.nn as nn


class APEC(nn.Module):
    """
    APEC (Asymmetric Parametric Exponential Curvature) activation function.
    """

    def __init__(
        self,
        constraints_alpha: list[float] = [-2.0, +2.0],
        constraints_beta: list[float] = [-2.5, +2.5],
        constraints_gamma: list[float] = [-2.5, -0.25],
        eps: float = 1.0e-5,
        std: float = 0.35,
        constrained: bool = True,
    ) -> None:
        super(APEC, self).__init__()

        # Init control params.
        self.constraints_alpha = constraints_alpha
        self.constraints_beta = constraints_beta
        self.constraints_gamma = constraints_gamma
        self.eps = eps
        self.std = std
        self.constrained = constrained

        # Init coefficients.
        alpha = torch.empty([1])
        alpha = torch.nn.init.normal_(
            alpha,
            mean=sum(self.constraints_alpha) / 2.0,
            std=self.std,
        )
        beta = torch.empty([1])
        beta = torch.nn.init.normal_(
            beta,
            mean=sum(self.constraints_beta) / 2.0,
            std=self.std,
        )
        gamma = torch.empty([2])
        gamma = torch.nn.init.normal_(
            gamma,
            mean=sum(self.constraints_gamma) / 2.0,
            std=self.std,
        )

        coefficients = torch.cat([alpha, beta, gamma], dim=0)
        coefficients = torch.nn.Parameter(coefficients)
        self.register_parameter("coefficients", coefficients)

        # Init constraints.
        if self.constrained:
            self.register_parameter_constraint_hooks()

        pass

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        a = self.coefficients[0]
        b = self.coefficients[1]
        g = self.coefficients[2]
        x = a + (b - x) / ((g - torch.exp(-x)) + self.eps)
        return x

    def enforce_coefficients_constraints(self) -> None:
        with torch.no_grad():
            self.coefficients[0].clamp_(
                self.constraints_alpha[0],
                self.constraints_alpha[1],
            )
            self.coefficients[1].clamp_(
                self.constraints_beta[0],
                self.constraints_beta[1],
            )
            self.coefficients[2].clamp_(
                self.constraints_gamma[0],
                self.constraints_gamma[1],
            )
        pass

    def register_parameter_constraint_hooks(self) -> None:
        self.coefficients.register_hook(
            lambda grad: self.enforce_coefficients_constraints()
        )
        pass

from torch import Tensor, nn


class Model(nn.Module):
    def forward(self, x: Tensor) -> Tensor:
        return x

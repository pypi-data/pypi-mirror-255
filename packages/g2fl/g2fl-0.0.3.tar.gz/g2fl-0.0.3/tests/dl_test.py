import torch

from g2fl import dl


def test_synthetic_data():
    true_w = torch.tensor([2, -3.4])
    true_b = 4.2
    features, labels = dl.synthetic_data(true_w, true_b, 1000)
    assert len(labels) == 1000
    assert len(features) == 1000

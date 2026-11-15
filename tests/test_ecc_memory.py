import pytest
import torch
from ecc_memory import ECCMemory, create_ecc_memory

class TestECCMemory:
    def test_init(self):
        m = ECCMemory(dim=256, hidden_dim=512)
        assert m.dim == 256
    
    def test_forward(self):
        m = ECCMemory(dim=256)
        x = torch.randn(32, 256)
        assert m(x).shape == (32, 256)
    
    def test_factory(self):
        m = create_ecc_memory()
        assert isinstance(m, ECCMemory)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

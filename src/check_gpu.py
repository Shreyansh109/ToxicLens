"""Checks that PyTorch can use the GPU, including half precision (fp16).

Run from the project root:
    python -m src.check_gpu
"""
import torch

print("PyTorch version:", torch.__version__)
print("Built for CUDA:", torch.version.cuda)
print("GPU available:", torch.cuda.is_available())

if torch.cuda.is_available():
    props = torch.cuda.get_device_properties(0)
    print("GPU name:", props.name)
    print("GPU memory (GB):", round(props.total_memory / 1024**3, 1))
    print("Compute capability:", torch.cuda.get_device_capability(0))
    print("Architectures in this build:", torch.cuda.get_arch_list())

    x = torch.randn(2000, 2000, device="cuda")
    y = x @ x
    torch.cuda.synchronize()
    print("Full precision test worked, result shape:", tuple(y.shape))

    xh = x.half()
    yh = xh @ xh
    torch.cuda.synchronize()
    print("Half precision (fp16) test worked, contains NaN:", bool(torch.isnan(yh).any()))
else:
    print("PyTorch cannot see the GPU. Send me this output.")
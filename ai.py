import torch

# 텐서 생성
x = torch.tensor([1.0, 2.0, 3.0])
print("Tensor on CPU:", x)

# 텐서를 GPU로 이동
if torch.cuda.is_available():
    x = x.to("cuda")
    print("Tensor on GPU:", x)
else:
    print("CUDA is not available.")

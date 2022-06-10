import albumentations as A
import albumentations.pytorch
from model.config import Config


image_transform = A.Compose([
    A.Resize(Config.image_size, Config.image_size),
    A.Normalize(),
    A.pytorch.transforms.ToTensorV2()
])

import os


class Config:
    DATA_DIR = './'
    CSV_PATH = os.path.join(DATA_DIR, 'finnal_the_clean.csv')
    train_batch_size = 4
    val_batch_size = 4
    num_workers = 4
    image_size = 512
    output_dim = 512
    hidden_dim = 512
    input_dim = 3
    epochs = 35
    lr = 1e-4
    num_of_classes = 7468
    pretrained = True
    model_name = 'resnet101'
    seed = 42

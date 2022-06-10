from pytorch_lightning.utilities.seed import seed_everything
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from model.dolg_wrapper import DolgNet
from config import Config


if __name__ == '__main__':
    seed_everything(Config.seed)

    model = DolgNet(
        input_dim=Config.input_dim,
        hidden_dim=Config.hidden_dim,
        output_dim=Config.output_dim,
        num_of_classes=Config.num_of_classes
    )

    checkpoint_callback = ModelCheckpoint(monitor="train_loss", dirpath='./logs', filename='mymodel-{epoch:02d}-{train_loss:.2f}')

    trainer = Trainer(gpus=1, max_epochs=Config.epochs, callbacks=[checkpoint_callback])

    trainer.fit(model)

    trainer.save_checkpoint('./logs/last_weight.ckpt')

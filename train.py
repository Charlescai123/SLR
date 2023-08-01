import sys,os
import matplotlib.pyplot as plt
import numpy as np
from TrainDataReader import DataGenerator
from keras.optimizers import SGD
from keras.models import Model,load_model
from keras.callbacks import CSVLogger, ModelCheckpoint, EarlyStopping,ReduceLROnPlateau

from model import c3d_model

def plot_history(history, result_dir):
    plt.plot(history.history['acc'], marker='.')
    plt.plot(history.history['val_acc'], marker='.')
    plt.title('model accuracy')
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.grid()
    plt.legend(['acc', 'val_acc'], loc='lower right')
    plt.savefig(os.path.join(result_dir, 'model_accuracy.png'))
    plt.close()

    plt.plot(history.history['loss'], marker='.')
    plt.plot(history.history['val_loss'], marker='.')
    plt.title('model loss')
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.grid()
    plt.legend(['loss', 'val_loss'], loc='upper right')
    plt.savefig(os.path.join(result_dir, 'model_loss.png'))
    plt.close()


def save_history(history, result_dir):
    loss = history.history['loss']
    acc = history.history['acc']
    val_loss = history.history['val_loss']
    val_acc = history.history['val_acc']
    nb_epoch = len(acc)

    with open(os.path.join(result_dir, 'result.txt'), 'w') as fp:
        fp.write('epoch\tloss\tacc\tval_loss\tval_acc\n')
        for i in range(nb_epoch):
            fp.write('{}\t{}\t{}\t{}\t{}\n'.format(
                i, loss[i], acc[i], val_loss[i], val_acc[i]))
        fp.close()

    param={'index':'data_record','test':0.2,'num_classes':36}
    generator=DataGenerator(param)

    print("\nNow Gnenrate model\n")

    if os.path.exists(os.path.join('model_checkpoint','model_save')):
        print("Continue Training")
        model=load_model(os.path.join('model_checkpoint','model_save'))
    else:
        print("New Training")

        input_shape=generator.feature_shape
        output_classes=generator.number_classes

        model_param={'input_shape':input_shape,'num_classes':output_classes,'weight_decay':0.005}
        model=c3d_model(model_param)

        lr = 0.005
        sgd = SGD(lr=lr, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        model.summary()

    print("\nNow fit model\n")



patience = 50
early_stop = EarlyStopping('val_loss', patience=patience)
reduce_lr = ReduceLROnPlateau('val_loss', factor=0.1,patience=int(patience/4), verbose=1)
model_names = os.path.join('model_checkpoint','model_checkpoint') + '.{epoch:02d}-{val_acc:.2f}.hdf5'
model_checkpoint = ModelCheckpoint(model_names, 'val_loss', verbose=1,save_best_only=True)

callbacks=[model_checkpoint,early_stop,reduce_lr]

history=model.fit_generator(
    generator.genTrainBatch(16),
    validation_data=generator.genTestBatch(16),
#    callbacks=callbacks,
    validation_steps=10,
    steps_per_epoch=10,
    epochs=30,
    verbose=1)

model.save(os.path.join('model_checkpoint','model_save'))
save_history(history,'model_checkpoint')
plot_history(history,'model_checkpoint')

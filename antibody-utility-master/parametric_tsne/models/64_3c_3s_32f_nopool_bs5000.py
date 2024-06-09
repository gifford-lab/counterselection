"function (and parameter space) definitions for hyperband"
"binary classification with Keras (multilayer perceptron)"

from os.path import join
import subprocess, h5py
from common_defs import *

# a dict with x_train, y_train, x_test, y_test

from keras.models import Sequential
from keras.constraints import max_norm
from keras.layers.core import Dense, Dropout, Flatten, Activation
from keras.layers.normalization import BatchNormalization as BatchNorm
from keras.layers.convolutional import ZeroPadding2D, Conv2D
from keras.layers import GlobalMaxPooling2D
from keras.callbacks import EarlyStopping
from keras.layers.advanced_activations import *
from keras.optimizers import Adam

from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, MaxAbsScaler

BS = 5000
W_maxnorm = 3
space = {
	'DROPOUT': hp.choice( 'drop', ( 0.3,0.5,0.7)),
	'ADAM_LR': hp.choice( 'adam_lr', ( 1e-02,1e-03,1e-04)),
}


def get_params():
	params = sample( space )
	return handle_integers( params )


def print_params( params ):
	pprint({ k: v for k, v in params.items() if not k.startswith( 'layer_' )})
	print


def try_params( n_iterations, params, data=None, datamode='memory'):

	print "iterations:", n_iterations
	print_params( params )

        batchsize = 100
        X_train, Y_train = data['train']
        X_valid, Y_valid = data['valid']
        inputshape = X_train.shape[1:]

        model = Sequential()
	model.add(Conv2D(64, (1, 3), padding='same', input_shape=inputshape, activation='relu', kernel_constraint=max_norm(W_maxnorm)))
	model.add(Conv2D(128, (1, 3), padding='same', activation='relu', kernel_constraint=max_norm(W_maxnorm)))
	model.add(Conv2D(256, (1, 3), padding='same', activation='relu', kernel_constraint=max_norm(W_maxnorm)))
        model.add(Flatten())

        model.add(Dense(32,activation='relu'))
        model.add(Dropout(params['DROPOUT']))
        model.add(Dense(2))

        optim = Adam
        myoptimizer = optim(lr=params['ADAM_LR'])
        mylossfunc = tsne
        model.compile(loss=mylossfunc, optimizer=myoptimizer)

        early_stopping = EarlyStopping( monitor = 'val_loss', patience = 10, verbose = 0 )

        model.fit(
                X_train,
                Y_train,
                batch_size=BS,
                epochs=int( round( n_iterations )),
                validation_data=(X_valid, Y_valid),
                callbacks = [ early_stopping ],
                shuffle=False)

        score = model.evaluate(X_train,Y_train, batch_size=BS)

	return { 'loss': score, 'model': (model.to_json(), optim, myoptimizer.get_config(), mylossfunc) }


def tsne(P, activations):
#     d = K.shape(activations)[1]
    d = 2 # TODO: should set this automatically, but the above is very slow for some reason
    n = BS  # TODO: should set this automatically
    v = d - 1.
    eps = K.variable(10e-15) # needs to be at least 10e-8 to get anything after Q /= K.sum(Q)
    sum_act = K.sum(K.square(activations), axis=1)
    Q = K.reshape(sum_act, [-1, 1]) + -2 * K.dot(activations, K.transpose(activations))
    Q = (sum_act + Q) / v
    Q = K.pow(1 + Q, -(v + 1) / 2)
    Q *= K.variable(1 - np.eye(n))
    Q /= K.sum(Q)
    Q = K.maximum(Q, eps)
    C = K.log((P + eps) / (Q + eps))
    C = K.sum(P * C)
    return C


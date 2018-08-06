import chainer
from chainer.optimizers import Adam
from chainer.iterators import SerialIterator
from chainer.training import extensions
import pandas as pd
#from lossfunction import LossSumMSE
#from network import LSTM
#from updater import UpdaterLSTM
from sklearn.model_selection import train_test_split
#import numpy as np
from chainer import training, cuda

from chainer import Reporter
from chainer import training
from chainer import Variable, reporter
import datetime
import numpy as np
import matplotlib.pylab as plt
from chainer import Chain, Variable, cuda, optimizer, optimizers, serializers
import chainer.functions as F
import chainer.links as L
from sklearn.preprocessing import MinMaxScaler
import os

def scale(X_train, X_val, y_train, y_val):
    # change type
    X_train = X_train.astype(np.float32)
    X_val   =   X_val.astype(np.float32)
    y_train = y_train.astype(np.float32)
    y_val   =   y_val.astype(np.float32)

    # scale inputs
    sclr = MinMaxScaler()
    X_train = sclr.fit_transform(X_train)
    X_val   = sclr.transform(X_val)

    # scale labels
    ysclr = MinMaxScaler()
    y_train = ysclr.fit_transform(y_train)
    y_val   = ysclr.transform(y_val)

    return X_train, X_val, y_train, y_val, sclr, ysclr
class RNN_LSTM(Chain):
    def __init__(self, units):
        # クラスの初期化
        # :param in_size: 入力層のサイズ
        # :param hidden_size: 隠れ層のサイズ
        # :param out_size: 出力層のサイズ
        super(RNN_LSTM, self).__init__()
        n_in = 7
        n_out = 1

        #with self.init_scope():

        lstms = [('lstn{}'.format(l), L.LSTM(None, n_unit))
                for l, n_unit in enumerate(units)]
        self.lstms = lstms
        for name, lstm in lstms:
            self.add_link(name, lstm)

        self.add_link('fc', L.Linear(units[-1],n_out))

    def __call__(self, x, t=None, train=False):
        # 順伝播の計算を行う関数
        # :param x: 入力値
        # :param t: 正解の予測値
        # :param train: 学習かどうか
        # :return: 計算した損失 or 予測値
        h = x
        for name, lstm in self.lstms:
            #print(h)
            h = lstm(h)
        return self.fc(h)

    def reset_state(self):
        # 勾配の初期化とメモリの初期化
        for name, lstm in self.lstms:
            lstm.reset_state()

class UpdaterLSTM(training.StandardUpdater):
    def __init__(self, itr_train, optimizer, device):
        super(UpdaterLSTM, self).__init__(itr_train, optimizer, device = device)

    def update_core(self):
        itr_train = self.get_iterator('main')
        optimizer = self.get_optimizer('main')

        batch = itr_train.__next__()
        X_STF, y_STF = chainer.dataset.concat_examples(batch,self.device)

        optimizer.target.zerograds()
        optimizer.target.predictor.reset_state()
        loss = optimizer.target(Variable(X_STF), Variable(y_STF))

        loss.backward()
        optimizer.update()

class LossSumMSE(L.Classifier):
    def __init__(self, predictor):
        super(LossSumMSE, self).__init__(predictor, lossfun=F.mean_squared_error)
        #self.reporter = Reporter()

    def __call__(self, X_STF, Y_STF):
        #print(X_STF)
        X_TSF = X_STF.transpose(1,0,2)
        #print(X_TSF)
        y_TSF = Y_STF.transpose(1,0,2)
        #print(y_TSF.shape)
        seq_len = X_TSF.shape[0]
        #print(seq_len)

        loss = 0
        for t in range(seq_len):
            #print(X_TSF[t])
            pred = self.predictor(X_TSF[t])
            obs = y_TSF[t]
            #print(pred, obs)
            loss += self.lossfun(pred, obs)
        loss /= seq_len
        #print(loss)

        reporter.report({'loss': loss},self)

        return loss
gpu_device = 0
cuda.get_device(gpu_device).use()
# model
#startepoch = 141
#weight_file = os.path.join('results', 'model_epoch-{}'.format(startepoch))
units = (7,5,3)
network = RNN_LSTM(units)
#serializers.load_npz(weight_file, network)
model = LossSumMSE(network)


# optimizer
optimizer = Adam()
optimizer.setup(model)

model.to_gpu(gpu_device)
xp = cuda.cupy

# dataset (Datasetオブジェクトじゃなくて、list(zip())でも可)
df = pd.read_csv('datas_log.csv')
# 1ではなく1:とするのは、shapeを(144,)ではなく(144,1)とするため
#print(df)
y = df.iloc[:,0:1].values
X = df.iloc[:,1:].values
print(y)
print(X)
#series = df.iloc[:,1:].values
#diffed = difference(series)
#X, y = supervise(diffed)
X_train, X_val, y_train, y_val = train_test_split(X, y,
                                                  test_size=0.3,
                                                  shuffle=False)
X_train, X_val, y_train, y_val, sclr, ysclr = scale(X_train, X_val, y_train, y_val)
# change type
X_train = X_train.astype(xp.float32)
X_val   =   X_val.astype(xp.float32)
y_train = y_train.astype(xp.float32)
y_val   =   y_val.astype(xp.float32)
# change shape
#print(X_train)
#print(X_val)
#print(y_train)
#print(y_val)
X_train = X_train[xp.newaxis, :, :]
X_val   =   X_val[xp.newaxis, :, :]
y_train = y_train[xp.newaxis, :, :]
y_val   =   y_val[xp.newaxis, :, :]
ds_train = list(zip(X_train, y_train))
ds_val   = list(zip(X_val  , y_val  ))
print(len(ds_train[0][0]))
print(len(ds_val[0][0]))
# iterator
itr_train = SerialIterator(ds_train, batch_size=10, shuffle=False)
itr_val   = SerialIterator(ds_val  , batch_size=10, shuffle=False, repeat=False)

# updater
updater = UpdaterLSTM(itr_train, optimizer, device = gpu_device)

# trainer
trainer = training.Trainer(updater, (100000, 'epoch'), out='results')
# evaluation
eval_model = model.copy()
eval_rnn = eval_model.predictor
trainer.extend(extensions.Evaluator(
            itr_val, eval_model, device=gpu_device,
            eval_hook=lambda _: eval_rnn.reset_state()))
# other extensions
trainer.extend(extensions.LogReport())
trainer.extend(extensions.snapshot_object(model.predictor,
                                           filename='model_epoch-{.updater.epoch}'))
trainer.extend(extensions.PrintReport(
                ['epoch','main/loss','validation/main/loss']
            ))

trainer.run()

import os
from chainer import serializers, Chain
#from Training import scale, RNN_LSTM
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import chainer.links as L

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
        n_in = 6
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

#best_idx = log['validation/main/loss'].argmin()
#best_epoch = int(log['epoch'].ix[best_idx])
df = pd.read_csv('datas_log.csv')

y = df.iloc[:,0:1].values
X = df.iloc[:,1:].values
X_train, X_val, y_train, y_val = train_test_split(X, y,
                                                  test_size=0.3,
                                                  shuffle=False)
X_train, X_val, y_train, y_val, sclr, ysclr = scale(X_train, X_val, y_train, y_val)

X_train = X_train.astype(np.float32)
X_val   =   X_val.astype(np.float32)
y_train = y_train.astype(np.float32)
y_val   =   y_val.astype(np.float32)

X_train = X_train[np.newaxis, :, :]
X_val   =   X_val[np.newaxis, :, :]
y_train = y_train[np.newaxis, :, :]
y_val   =   y_val[np.newaxis, :, :]

n_train = X_train.shape[1]
n_val = X_val.shape[1]

X = np.concatenate((X_train, X_val), axis=1)[0]
obs = np.concatenate((y_train, y_val), axis=1)[0]

log = pd.read_json('results/log')
epoch = int(log['epoch'].ix[log['validation/main/loss'].argmin()])
units = (7, 5, 3)
model = RNN_LSTM(units)
weight_file = os.path.join('results', 'model_epoch-{}'.format(epoch))
serializers.load_npz(weight_file, model)

pred = []
print(X)
for X_t in X:
    #print(X_t.reshape(-1,6))
    p_t = model(X_t.reshape(-1,7)).data[0]
    pred.append(p_t)
"""
p_t = X_val[0,5]
n_pred = n_val
for t in range(n_pred):
    p_t = model(p_t.reshape(-1,6)).data[0]
    pred.append(p_t)
"""
obs_unscale = np.exp(ysclr.inverse_transform(obs))-30
pred_unscale = np.exp(ysclr.inverse_transform(pred))-30

plt.figure(figsize=(15,10))

plt.plot(obs, label='obs')
plt.plot(pred, label='pred')

plt.grid()
plt.legend()
plt.axvline(n_train, color='r')

plt.show()
plt.figure(figsize=(15,10))

plt.plot(obs_unscale, label='obs')
plt.plot(pred_unscale, label='pred')

plt.grid()
plt.legend()
plt.axvline(n_train, color='r')

plt.show()

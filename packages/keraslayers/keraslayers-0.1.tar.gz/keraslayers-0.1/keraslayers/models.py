import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Layer, LSTM, GRU, Bidirectional, Conv1D, MaxPooling1D, Dropout
from tensorflow.keras.callbacks import Callback
from keras.callbacks import Callback

class LSTMModel(Layer):
    def __init__(self, units, input_shape, activation='tanh', return_sequences=False, dropout=0.0, pt=False, **kwargs):
        super(LSTMModel, self).__init__(**kwargs)

        self.units_ = units
        self.input_shape_ = input_shape
        self.activation_ = activation
        self.return_sequences_ = return_sequences 
        self.lstm_layer = None 
        self.pt = pt
        objDpo = dpo() 
        self.dropout = objDpo.setVal(self.return_sequences_, input_shape[1], 2) 
        
        if (self.pt == True):
            print(("Model: LSTM, Input Shape: {} , Drop Out: {}").format(self.input_shape_[1], self.dropout))

        self.lstm_layer = LSTM(units=self.units_, input_shape=self.input_shape_, activation=self.activation_, return_sequences=self.return_sequences_, dropout = self.dropout)

    def call(self, inputs):
        return self.lstm_layer(inputs) 

class BiDirectionalLSTMModel(Layer):
    def __init__(self, units, input_shape, activation='tanh', return_sequences=False, dropout=0.0, pt=False, **kwargs):
        super(BiDirectionalLSTMModel, self).__init__(**kwargs)

        self.units_ = units
        self.input_shape_ = input_shape
        self.activation_ = activation
        self.return_sequences_ = return_sequences 
        self.bilstm_layer = None
        self.pt = pt
        objDpo = dpo() 
        self.dropout = objDpo.setVal(self.return_sequences_, input_shape[1],1) 

        if (self.pt == True):
            print(("Model: AttBiLSTM, Input Shape: {} , Drop Out: {}").format(self.input_shape_[1], self.dropout))

        self.bilstm_layer = Bidirectional(LSTM(self.units_, input_shape=self.input_shape_, activation=self.activation_, return_sequences=self.return_sequences_, dropout =  self.dropout))

    def call(self, inputs):
        return self.bilstm_layer(inputs) 

class GRUModel(Layer):
    def __init__(self, units, input_shape, activation='tanh', return_sequences=False, dropout = 0.0, pt=False, **kwargs):
        super(GRUModel, self).__init__(**kwargs)

        self.units_ = units
        self.input_shape_ = input_shape
        self.activation_ = activation
        self.return_sequences_ = return_sequences
        self.gru_layer = None
        self.pt = pt
        objDpo = dpo() 

        self.dropout = objDpo.setVal(self.return_sequences_, input_shape[1], 2) 

        if (self.pt == True):
            print(("Model: GRU, Input Shape: {} , Drop Out: {}").format(self.input_shape_[1], self.dropout))

        # GRU layer
        self.gru_layer = GRU(units=self.units_, input_shape=self.input_shape_, activation=self.activation_, return_sequences=self.return_sequences_, dropout = self.dropout)

    def call(self, inputs):
        return self.gru_layer(inputs) 

class CNNModel(Layer):
    def __init__(self, input_shape, filters=64, kernel_size=3, activation='relu', pool_size = 2, dropout = 0.0, pt=False, **kwargs):
        super(CNNModel, self).__init__(**kwargs)
        self.filters_ = filters
        self.input_shape_ = input_shape
        self.activation_ = activation
        self.kernel_size_ = kernel_size 
        self.pool_size_ = pool_size
        self.return_sequences_ = False
        self.cnn_layer = None
        self.pt = pt
        objDpo = dpo() 
        self.dropout = objDpo.setVal(self.return_sequences_, input_shape[1]) 

        # Add Conv1D layer
        self.conv1d_layer = Conv1D(filters=self.filters_, kernel_size=self.kernel_size_, activation=self.activation_, input_shape=self.input_shape_)

        # Add MaxPooling1D layer
        self.maxpooling1d_layer = MaxPooling1D(pool_size=2)

        # Add Dropout layer
        self.dropout_layer = Dropout(rate=self.dropout)

        if (self.pt == True):
            print(("*Model: CNN, Input Shape: {} , Drop Out: {}").format(self.input_shape_[1], self.dropout))

    def call(self, inputs, training=None, mask=None):
        # Forward pass
        x = self.conv1d_layer(inputs)
        x = self.maxpooling1d_layer(x)
        x = self.dropout_layer(x, training=training)

        return x
    

# Custom layer to apply (1 - tanh) to the input gate output
class TLSTMModel(Layer):
    def __init__(self, units, input_shape, activation='tanh', return_sequences=False, dropout=0.0, pt=False, **kwargs):
        super(TLSTMModel, self).__init__(**kwargs)
        self.units_ = units
        self.input_shape_ = input_shape
        self.activation_ = activation
        self.return_sequences_ = return_sequences   
        self.pt = pt
        objDpo = dpo() 
        self.dropout = objDpo.setVal(self.return_sequences_, input_shape[1]) 
        if (self.pt == True):
            print(("Model: TLSTM, Input Shape: {} , Drop Out: {}").format(self.input_shape_[1], self.dropout)) 

    def build(self, input_shape):
        input_dim = input_shape[-1]
        self.lstm = LSTM(units=self.units_, activation=self.activation_, return_sequences=self.return_sequences_, dropout = self.dropout)
        self.one_minus_tanh = tf.keras.layers.Lambda(lambda x: 1 - x, output_shape=(input_shape[1], self.units_))

        super(TLSTMModel, self).build(self.input_shape_) 
        
    def call(self, x):
        lstm_output = self.lstm(x)
        modified_output = self.one_minus_tanh(lstm_output)
        return modified_output

    def dpo(self):
        dpo_value = 0.0 if self.return_sequences_ else (0.4 if self.input_shape_[1] > 33 else 0.5)  
        return 0.2 if dpo_value == 0.0 and self.input_shape_[1] < 30 else dpo_value

class dpo:
    
    def setVal(self, rtn_seq, shp, tp=0):
      rtn_value = 0.0 
      if shp > 33 or shp == 3: 
        rtn_value = 0.4 
      else:
        rtn_value = 0.5 

      if (shp > 33 and tp==1):
        rtn_value = 0.4 

      if (shp == 33 and rtn_seq==True and tp==2):
        rtn_value = 0.3

      if ((shp == 21 or shp == 20 or shp == 16 or shp == 15 or shp == 3 or shp == 2) and rtn_seq==True and tp==2):
        rtn_value = 0.2

      if (shp ==34 and rtn_seq==True and tp==2):
        rtn_value = 0.0
        
        # Call the method 
      return rtn_value

class AccuracyCallback(Callback):
    def __init__(self, X_val, y_val):
        super().__init__()
        self.X_val = X_val
        self.y_val = y_val

    def on_epoch_end(self, epoch, logs=None):
        # Calculate accuracy on the validation set
        y_pred = np.round(self.model.predict(self.X_val).flatten())
        accuracy = np.mean(np.equal(self.y_val, y_pred))

        # Log accuracy in the metrics as a percentage
        logs["accuracy"] = accuracy * 100

class EarlyStop(Callback):
    def __init__(self, monitor='val_loss', patience=0, restore_best_weights=False):
        super(EarlyStop, self).__init__()
        self.monitor = monitor
        self.patience = patience
        self.restore_best_weights = restore_best_weights
        self.best_value = float('inf')
        self.wait = 0
        self.stopped_epoch = 0
        self.stopped_training = False
        self.model = None  # Added to store the model

    def set_model(self, model):
        self.model = model

    def set_params(self, params):
        self.params = params

    def on_epoch_end(self, epoch, logs=None):
        current_value = logs.get(self.monitor)
        if current_value is None:
            raise ValueError(f" Early stopping monitor '{self.monitor}' not found in logs.")

        if current_value < self.best_value:
            self.best_value = current_value
            self.wait = 0
        else:
            self.wait += 1
            if self.wait >= self.patience:
                #print(f" Early Stopping: Stopped training at epoch {epoch} based on '{self.monitor}'")
                print(" ")
                self.stopped_epoch = epoch
                self.stopped_training = True

    def on_train_end(self, logs=None):
        if self.stopped_training and self.restore_best_weights:
            #print(" Early Stopping: Restoring best weights.") 
            print(" ") 

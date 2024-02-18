import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Layer, LSTM, GRU, Bidirectional, Conv1D, MaxPooling1D, Dropout
from tensorflow.keras.callbacks import Callback
from keras.callbacks import Callback
import pandas as pd
import json
import re
import cloudscraper
import requests
import os
import os.path
import datetime as dt
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from keras import backend as K

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
      if shp > 26: 
        rtn_value = 0.3
      elif shp == 3:
        rtn_value = 0.4
      else:
        rtn_value = 0.5

      if (shp > 26 and tp==1):
        rtn_value = 0.4

      if (shp == 26 and rtn_seq==True and tp==2):
        rtn_value = 0.3

      if ((shp == 13 or shp == 12 or shp == 20 or shp == 16 or shp == 15 or shp == 3 or shp == 2) and rtn_seq==True and tp==2):
        rtn_value = 0.2

      if (shp == 25 and rtn_seq==True and tp==2):
        rtn_value = 0.1

      if (shp ==27 and rtn_seq==True and tp==2):
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

class utilities:
    def fromattedDate(self, dataDay, value_inside):
        is_valid_date = True

        try:
            datetime.strptime(value_inside, '%Y.%m.%d')
        except ValueError:
            is_valid_date = False

        if not is_valid_date:
            value_inside = value_inside.strip()
            data_day_formatted = ""
            arr_data_day = dataDay.split('.')
            str_data_date = arr_data_day[1] + ' ' + arr_data_day[0]
            data_day_obj = datetime.strptime(str_data_date, '%Y %b')
            arr_row_date = value_inside.split(' ')
            row_date = ""
            if len(arr_row_date) > 1:
                row_date = arr_row_date[1]
                data_day_formatted = data_day_obj.strftime("%Y") + '.' + data_day_obj.strftime("%m") + '.' + row_date
        else:
            data_day_formatted = value_inside

        return data_day_formatted

    def parse_data(self, dataDay):

        # Data Extraction
        url = 'https://www.forexfactory.com/calendar?month={dataDay}'.format(dataDay=dataDay)

        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})

        #scraper = cloudscraper.create_scraper()
        source = scraper.get(url).text
        soup = BeautifulSoup(source, 'html.parser')

        # Data manipulation
        date_str = ""
        value_list_filtered = []

        data_table = soup.find('table', class_='calendar__table')
        value_list = []

        for row in data_table.find_all("tr"):
            row_data = list(filter(None, [td.text for td in row.find_all("td")]))
            if row_data and not "\xa0" in row_data and not "No Data Series" in row_data:
                value_list.append(row_data)

        for value in value_list:
            i_value_list = 0
            i_value = 0
            status = True
            for value_inside in value:
                value_inside = value_inside.strip()
                if "Actual" in value_inside or "Forecast" in value_inside or "Previous" in value_inside or "Bank Holiday" in value_inside:
                    status = False
                    break

                if i_value == 0 and value_inside.strip() != '':
                    date_str = self.fromattedDate(dataDay,value_inside)
                elif i_value == 0 and value_inside.strip() == '':
                    value_inside = date_str

                value[i_value] = value_inside.replace('\n', '').strip()
                i_value = i_value + 1

            i_value_list = i_value_list + 1

            if status == True:
                value[0] = self.fun_precisionfromattedDate(dataDay,value[0])
                value_list_filtered.append(value)

        return value_list_filtered

    def addToDataFrame(self, dataDay):
        df_temp = pd.DataFrame(self.parse_data(dataDay))
        df_temp = df_temp[df_temp[1].isnull() == False]

        df = pd.DataFrame()

        df["Date"] = df_temp[0]
        df["Currency"] = df_temp[3]
        df["Title"] = df_temp[5]
        df["Actual"] = df_temp[7]
        df["Focus"] = df_temp[8]
        df["Previous"] = df_temp[9]
        df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d', errors='coerce')
        df['Date'] = df['Date'].dt.strftime('%Y.%m.%d')
        df = pd.DataFrame(df).sort_values('Date', ascending=True)
        #df.set_index('Date', inplace=True)
        del(df_temp)
        return df

    def switch(self, m):
        if m == 1:
            return "Jan"
        elif m == 2:
            return "Feb"
        elif m == 3:
            return "Mar"
        elif m == 4:
            return "Apr"
        elif m == 5:
            return "May"
        elif m == 6:
            return "Jun"
        elif m == 7:
            return "Jul"
        elif m == 8:
            return "Aug"
        elif m == 9:
            return "Sep"
        elif m == 10:
            return "Oct"
        elif m == 11:
            return "Nov"
        elif m == 12:
            return "Dec"

    def scrape_forexfactory_calendar(self, year_list):
        dfs = []
        for i in year_list:
            for j in range(12):
                dataDay = self.switch(j+1) + "." + i
                df = self.addToDataFrame(dataDay)
                if df is not None:
                    dfs.append(df)

        df_combined = pd.concat(dfs, ignore_index=True)
        return df_combined

    def convertValue(self, x):
        x = str(x)
        x = x.replace("<", "")
        x = x.replace(">", "")

        rtn = x

        if x.find('%') > 0:
            rtn = float(x.strip('%'))/100
        elif x.upper().find('K') > 0:
            rtn = float(x.strip('K'))
        elif x.upper().find('B') > 0:
            rtn = float(x.strip('B'))
        else:
            rtn = float(rtn)
        return rtn

    def isNumeric(self, s):
        try:
            complex(s)
            return True
        except ValueError:
            return False 

    # Get Model History
    def getHistory(self, file_name):
      f = open(file_name)
      data = json.load(f)
      f.close()
      return data

    def FS_calendar_USD(self, FS_calendar_data_USD_normalize):
      tmp_FS_calendar_data_USD_normalize = FS_calendar_data_USD_normalize.drop(columns=["Advance GDP Price Index q/q (USD)","Advance GDP q/q (USD)","CB Consumer Confidence (USD)","Chicago PMI (USD)","Consumer Credit m/m (USD)","Federal Budget Balance (USD)","Federal Funds Rate (USD)","Final GDP Price Index q/q (USD)","Flash Manufacturing PMI (USD)","Flash Services PMI (USD)","Prelim GDP Price Index q/q (USD)","Prelim GDP q/q (USD)","Prelim UoM Consumer Sentiment (USD)","Prelim UoM Inflation Expectations (USD)","Revised UoM Consumer Sentiment (USD)","Revised UoM Inflation Expectations (USD)","Final Services PMI (USD)","Unemployment Rate (USD)","CPI y/y (USD)", "Final GDP q/q (USD)","PPI m/m (USD)"])
      return tmp_FS_calendar_data_USD_normalize

    def FS_calendar_GBP(self, FS_calendar_data_GBP_normalize):
      tmp_FS_calendar_data_GBP_normalize = FS_calendar_data_GBP_normalize.drop(columns=["GfK Consumer Confidence (GBP)","NIESR GDP Estimate (GBP)","Nationwide Consumer Confidence (GBP)","Prelim GDP q/q (GBP)","Second Estimate GDP q/q (GBP)","PPI Input m/m (GBP)", "PPI Output m/m (GBP)","Final Services PMI (GBP)"])
      return tmp_FS_calendar_data_GBP_normalize

    # Calculate F1 Score
    def fun_recall(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.float64)
        y_pred = tf.cast(y_pred, tf.float64)
        y_true = K.ones_like(y_true)
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        all_positives = K.sum(K.round(K.clip(y_true, 0, 1)))

        recall = true_positives / (all_positives + K.epsilon())
        return recall

    def fun_precision(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.float64)
        y_pred = tf.cast(y_pred, tf.float64)
        y_true = K.ones_like(y_true)
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))

        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision

    def fun_f1_score(self, y_true, y_pred):
        val_precision = self.fun_precision(y_true, y_pred)
        val_recall = self.fun_recall(y_true, y_pred)
        return 2*(val_precision*val_recall)/(val_precision+val_recall)

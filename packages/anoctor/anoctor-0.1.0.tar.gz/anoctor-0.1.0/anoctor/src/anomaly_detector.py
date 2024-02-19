# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 19:04:00 2024

@author: Q631031
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 14:06:04 2024

@author: Q631031
"""
#!/bin/env python3
print('Run: pip install pipreqs and pip install -r requirements.txt')

import os
import pandas as pd
from datetime import time as dt
from datetime import timedelta as dt
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#%matplotlib inline
#from sklearn.cluster import DBSCAN
#from sklearn.preprocessing import LabelEncoder
#from sklearn.impute import KNNImputer
#from sklearn.metrics import mean_squared_error
#tensorFlow and Keras for building the autoencoder model
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Input, Dropout, Dense, LSTM, TimeDistributed, RepeatVector, Flatten, GRU, concatenate
#from sklearn.model_selection import train_test_split
from copy import deepcopy
from tensorflow.keras import optimizers
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Sequential, Model
import keras.backend as K
from argparse import ArgumentParser
from keras.callbacks import EarlyStopping
from numpy.random import seed
#from tensorflow import set_random_seed
#tf.logging.set_verbosity(tf.logging.ERROR)
from keras.models import Model
from keras import regularizers
import warnings
warnings.filterwarnings("ignore")
import joblib
import PySimpleGUI as sg
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import sys

sg.theme("DarkBlue")
font1 = ("Arial", 10)
font2 = ("Arial", 11, 'bold', 'underline')
sg.set_options(font=font1)
icon=r"icons\bmw.ico"

def make_win1():
    
    
    single_signal = [
        "",
        "Anzeige_Ladezustand_Hochvoltspeicher",
        "Status_Verriegelung_Ladestecker",
        "Status_Pilot",
        "NM3BasePartialNetworks",
        "NM3FunctionalPartialNetworks",
        "ActualValueVoltageLinkVerified",
        "MessIdCcuEndOfLineTest",
        "MessIdCcuEndOfLineTestNo2",
        "MessIdCCUEndOfLineTestNo3",
        "ActualValueVoltageHighStorage",
        "Custom Signal",
    ]
    actv_sgn = [
        "Sigmoid", "Tanh", "Rectified Linear Unit" 

    ]
    layout = [
        [sg.T("")],
        [sg.Text("Status_Laden input file:   "),
         sg.Input(key="-IN-"),
         sg.FileBrowse(file_types=(("ALL CSV Files", "*.csv"), ("ALL Files", "*.csv*"), ))],
        [sg.T("")],
        [sg.Text("Choose Single Signal:     "),
        sg.Combo(single_signal, key="inp", size=(40,4), enable_events=True, readonly=True)],
        [sg.T("")],
        [sg.Text("Signal input file:              "),
         sg.Input(key="signinp"),
         sg.FileBrowse(file_types=(("ALL CSV Files", "*.csv"), ("ALL Files", "*.csv*"), ))],
        [sg.T("")],
        [sg.Text("Threshold Value:             "), sg.Input(key='thresh_val', size=8)],
        [sg.T("")],
        [sg.Text("Choose Multiple Signals:"), sg.Checkbox('', default=False, key='chk', enable_events=True)],
        [sg.T("")],
        [sg.Text("Activation Function:         "),
        sg.Combo(actv_sgn, key="actv_sgn", size=(20,4), enable_events=True, readonly=True, default_value= 'Sigmoid')],
        [sg.T("")],
        [sg.Text("Output Folder/Filename:  "),
         sg.Input(key="output_folder", tooltip= ' Choose a folder or filename(.pdf) or leave it blank '),
         sg.FolderBrowse()],
        [sg.T("")],
        [sg.Text("Custom Signal", text_color='#00ffef', font=font2)],
        [sg.T("")],
        [sg.Text("Signal Range:                 "), sg.Input(key='cust_text', size=8, disabled=True, disabled_readonly_background_color="Gray")],
        [sg.T("")],
        [sg.Text("Required Bytes:              "), sg.Input(key='cust_byte', size=8, disabled=True, disabled_readonly_background_color="Gray", tooltip=" Eg: 2,5 or 2,3,5 or 2,3,4,5 ")],
         [sg.T("")],
        [sg.T("")],
        [sg.Button('Submit',pad=(300, 0),key='submitorg')],
    ]
    
    return sg.Window('Anomaly Detection Analysis', layout, size=(700,680),  enable_close_attempted_event=True, finalize=True, icon=icon)


def make_win2():
    
    
    signal1= [
        "",
        "NM3BasePartialNetworks",
        "NM3FunctionalPartialNetworks",
        "MessIdCcuEndOfLineTest",
        "MessIdCcuEndOfLineTestNo2",
        "MessIdCCUEndOfLineTestNo3",
        "ActualValueVoltageLinkVerified",
        "ActualValueVoltageHighStorage",
    ]
    

    layout = [[sg.Text("Please leave the third dropdown as it is, if you want to analyse only two signals.", text_color='yellow')],
              [sg.T("")],
              [sg.Text("Choose Signal1:          "),
              sg.Combo(signal1, key="inp1", size=(35,4), enable_events=True, readonly=True)],
              [sg.Text("Select Signal1 File:     "),
               sg.Input(key="sgl1inp", size=(37,4)),
               sg.FileBrowse(file_types=(("ALL CSV Files", "*.csv"), ("ALL Files", "*.csv*"),))],
              [sg.Text("Threshold Value1:       "), sg.Input(key='thresh_val1', size=8)],
              [sg.T("")],
              [sg.Text("Choose Signal2:         "),
              sg.Combo(signal1, key="inp2", size=(35,4), enable_events=True, readonly=True)],
              [sg.Text("Select Signal2 File:    "),
               sg.Input(key="sgl2inp", size=(37,4)),
               sg.FileBrowse(file_types=(("ALL CSV Files", "*.csv"), ("ALL Files", "*.csv*"), ))],
              [sg.Text("Threshold Value2:      "), sg.Input(key='thresh_val2', size=8)],
              [sg.T("")],
              [sg.Text("Choose Signal3:         "),
              sg.Combo(signal1, key="inp3", size=(35,4), enable_events=True, readonly=True, disabled=False)],
              [sg.Text("Select Signal3 File:    "),
               sg.Input(key="sgl3inp", size=(37,4)),
               sg.FileBrowse(file_types=(("ALL CSV Files", "*.csv"), ("ALL Files", "*.csv*"), ))],
              [sg.Text("Threshold Value3:      "), sg.Input(key='thresh_val3', size=8)],
              [sg.T("")],
              [sg.Button('Submit',pad=(300, 0), key='submitmul')]]
    
    return sg.Window('Signals for Simulatneous Analysis', layout, size=(700,450), enable_close_attempted_event=True, finalize=True, icon=icon)


def main_window():
    filename_charg_act= ''
    setting= ''
    filename_signal1= ''
    byte_range= ''
    byte_req= ''
    sig1= ''
    sig2= '' 
    sig3= ''
    filename_sig1= '' 
    filename_sig2= '' 
    filename_sig3='' 
    actvtn_sgnl= ''  
    threshold_val_sig1= ''
    chk_flg= False 
    threshold_val_mul_sig1= ''
    threshold_val_mul_sig2= ''
    threshold_val_mul_sig3= ''
    output_folder= ''
    
    window1, window2 = make_win1(), None

    while True:             # Event Loop
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED and sg.popup_yes_no('Do you really want to exit?', title='Exit', icon=icon) == 'Yes':
            if window== window1 and window2!= None:
                window2.close()
                window1.close()
                window2=None
                window1=None
                return False
                break
            elif window == window2 and window2!= None:       # if closing win 2, mark as closed
                window2.close()
                window1['chk'].Update(value=False)
                window2=None
            elif window == window1:  
                window1.close() # if closing win 1, mark as closed
                return False
                break
        elif event == 'chk' and window2==None:
                window2 = make_win2()
                window2.move(window1.current_location()[0], window1.current_location()[1] + 220)
        elif event == 'chk'and values["chk"] == False and window!= None:
            window2.close()
            window2=None
            window1['chk'].Update(value=False)
        elif event == 'inp':
           setting = values["inp"]
           if setting == 'Custom Signal':
                window1['cust_text'].update(disabled=False)
                window1['cust_byte'].update(disabled=False)
           else:
               window1['cust_text'].update(disabled=True)
               window1['cust_byte'].update(disabled=True)
           if setting != '':
              window1['chk'].Update(disabled=True)
           else:
              window1['chk'].Update(disabled=False)


        elif event == "submitmul":
            sig1 = values["inp1"]
            sig2 = values["inp2"]
            sig3 = values["inp3"]
            filename_sig1 = values['sgl1inp']
            filename_sig2 = values['sgl2inp']
            filename_sig3 = values['sgl3inp']
            threshold_val_mul_sig1= values['thresh_val1']
            threshold_val_mul_sig2= values['thresh_val2']
            threshold_val_mul_sig3= values['thresh_val3']

            if (sig1 and sig2) == '' or sig2=='':
                sg.popup('Invalid Selection!! Select atleast two signals!           ', title='No Output   ')
            elif (filename_sig1 and filename_sig2) == '' or filename_sig2=='':
                sg.popup('Invalid Selection!! Please select the files!           ', title='No Output   ')
            elif sig3!= '' and filename_sig3=='':
                sg.popup('Invalid Selection!! Please select the files!           ', title='No Output   ')
            else:
                chk_flg= True
                window1['inp'].Update(disabled=True)
                window1['chk'].Update(value=False)
                window1['chk'].Update(disabled=True)
                window2.close()
                window2=None
        elif event == "submitorg":
            filename_charg_act = values['-IN-']
            filename_signal1 = values['signinp']
            byte_range= values["cust_text"]
            byte_req= values["cust_byte"]
            actvtn_sgnl= values["actv_sgn"]
            threshold_val_sig1= values["thresh_val"]
            output_folder= values['output_folder']
            if setting=='' and chk_flg==False:
               sg.popup('No Valid Selections         ', title='No Input    ') 
            elif filename_signal1== '' and setting!= '':
               sg.popup('Invalid Selection!! Please select the files!           ', title='No Input    ') 
            #if threshol_val !='' or (setting!='' and chk_flg==False)
            else:
                window.close()
                break

    return [{'charging_file':filename_charg_act, 'single_signal': setting, 'single_signal_file':filename_signal1, 'activation_val': actvtn_sgnl, 'threshold_val': {setting: threshold_val_sig1} ,'byte_range':byte_range, 'byte_req':byte_req, 'output_file': output_folder}, {'check_flag':chk_flg,'mul_signal1':sig1, 'mul_signal1_file':filename_sig1, 'mul_signal2':sig2, 'mul_signal2_file':filename_sig2, 'mul_signal3':sig3, 'mul_signal3_file':filename_sig3, 'threshold_val': {sig1: threshold_val_mul_sig1, sig2: threshold_val_mul_sig2, sig3: threshold_val_mul_sig3}}] 
     

def assigning_values(signal_name):
        
    #if list[1]["check_flag"] == False:  
        
    if signal_name == "Anzeige_Ladezustand_Hochvoltspeicher":
        byte_range= 9
        byte_req = [6] 
    
    elif signal_name == "Status_Verriegelung_Ladestecker":
        byte_range= 9
        byte_req = [4]    
        
    elif signal_name == "Status_Pilot":
        byte_range= 9
        byte_req = [5]
        
    elif signal_name == "NM3BasePartialNetworks":
        byte_range= 9
        byte_req =[3,4]
        
    elif signal_name == "NM3FunctionalPartialNetworks":
        byte_range= 9
        byte_req =[5,6,7,8]
    
    elif signal_name == "ActualValueVoltageLinkVerified":
        byte_range= 13
        byte_req =[6,7]
        
    elif signal_name == "MessIdCcuEndOfLineTest":
        byte_range= 21
        byte_req = [20]

    elif signal_name == "MessIdCcuEndOfLineTestNo2":
        byte_range= 33
        byte_req =[31,32]
        
    elif signal_name == "MessIdCCUEndOfLineTestNo3":
        byte_range= 25
        byte_req =[4,5,6]
        
    elif signal_name == "ActualValueVoltageHighStorage":
        byte_range= 33
        byte_req =[30,31]
        
    elif signal_name == "Custom Signal":
        byte_range= int(sig_val[0]["byte_range"])+1
        bytes= str(sig_val[0]["byte_req"]).split(',')
        byte_req = [int(bytes)+1 for byte in bytes]
        
    return byte_range, byte_req

def read_csv(filename_analysis):
    df= pd.read_csv(filename_analysis, usecols=['tstamp', 'payload', 'frame_id', 'vehicle_vin'])
    df['timestamp'] = pd.to_datetime(df['tstamp'])
    df= df.drop(columns=['tstamp'])

    #byte_req = int(byte_req)
    #byte_req = [ int(x) for x in byte_req ]
    return df


#def plotTimeSeries():
    

def main(df, byte_range, byte_req):
    # df= pd.read_csv(filename_analysis, usecols=['tstamp', 'payload', 'frame_id', 'vehicle_vin'])
    # df['timestamp'] = pd.to_datetime(df['tstamp'])
    # df= df.drop(columns=['tstamp'])
    # print('main')
    #byte_req = int(byte_req)
    #byte_req = [ int(x) for x in byte_req ]
    #print((byte_req[0]))
    #print(df.head())
    K= []
    T1= []
    T2= []
    T3= []
    T4= []
    T5= []
    T6= []
    
    for i in df['payload']:
        A=''
        last_lis= []
        if isinstance(i, str):
            kl= list(i)
            #print(len(kl))
            for y in range(0, len(kl),2):
                a= str(kl[y])+str(kl[y+1])+' '
                A+=a
            K.append(A.strip())
            last_lis= A.strip().split(' ')
            if(len(last_lis)>= (int(byte_range))):
                
                if(len(byte_req)==1):
                    T1.append(last_lis[byte_req[0]])
                
                elif(len(byte_req)==2):
                    T1.append(last_lis[byte_req[0]])
                    T2.append(last_lis[byte_req[1]])
                         
                elif(len(byte_req)==3):
                    T1.append(last_lis[byte_req[0]])
                    T2.append(last_lis[byte_req[1]])
                    T3.append(last_lis[byte_req[2]])
                    
                elif(len(byte_req)==4):
                    T1.append(last_lis[byte_req[0]])
                    T2.append(last_lis[byte_req[1]])
                    T3.append(last_lis[byte_req[2]])
                    T4.append(last_lis[byte_req[3]])
                    
                else:
                    T1.append('00')
                    T2.append('00')
                    T3.append('00')
                    T4.append('00')
            
            else:
                T1.append('00')
                T2.append('00')
                T3.append('00')
                T4.append('00')

            
        else:
            T1.append('00')
            T2.append('00')
            T3.append('00')
            T4.append('00')

    # #################Saving extracted bytes into a dataframe df_last####################
           
    if(len(byte_req)==1):
       #T1 = [int(i) for i in test_list] 
       df_last_ini = pd.DataFrame(
            {'req_byte_1': T1      
            })            
                
                
    elif(len(byte_req)==2):         
       df_last_ini = pd.DataFrame(
           {'req_byte_1': T1,
            'req_byte_2': T2
           })  

    elif(len(byte_req)==3):     
      df_last_ini = pd.DataFrame(
          {'req_byte_1': T1,
           'req_byte_2': T2,
           'req_byte_3': T3
          })            
                
                
    elif(len(byte_req)==4):           
      df_last_ini = pd.DataFrame(
           {'req_byte_1': T1,
            'req_byte_2': T2,
            'req_byte_3': T3,
            'req_byte_4': T4
           })           
                
    else:
        T1.append(np.nan)
        T2.append(np.nan)
        T3.append(np.nan)
        T4.append(np.nan)
                   
                
                
     #################Conversion of required Bytes#######################

    ############For all bytes######################
    df_last=pd.DataFrame()
    df_conv_ini=pd.DataFrame()
    df_conv=pd.DataFrame()
    
    for i in range(1, len(df_last_ini.columns)+1):
          p=f"req_byte_{i}"
          df_last[p] = df_last_ini[p].apply(lambda x: int(str(x),16))
    
   
    if (df_last.values == 0).all():
        sys.exit('All Bytes are zero, nothing to process!')
        
    check_flag= False
    for i in range(1, len(df_last.columns)+1):
        q=f"req_byte_{i}"
        if (df_last[q] == 0).all():
            check_flag=True
            break    
        
    df_conv_ini= pd.DataFrame(data=df, index=None, columns=None, dtype=None, copy=None)
    df_conv_ini= df_conv_ini.drop(columns=['payload'])
    df_conv_ini= df_conv_ini.join(df_last)    
    
    if check_flag!= True:
        #replacing bytes 0 with Null value
        df_conv_ini.replace(0, np.nan, inplace=True)
        #drop null values
        df_conv_ini = df_conv_ini.dropna()
    
    #sorting indexes in ascending order
    df_conv_ini.sort_values(by='timestamp', inplace = True)
        
    #resetting indexes
    df_conv_ini= df_conv_ini.reset_index(drop=True)
    
    if df_conv_ini.empty:
        sys.exit('All Bytes are zero, nothing to process!')
    
    
    
    if (len(df_conv_ini.index)>500000):
    
        df_conv_ini['timestamp'] = pd.to_datetime(df_conv_ini['timestamp'])
        freq = '0.005Min'
        
        if(len(byte_req)==1):
              df_conv= df_conv_ini.groupby(['req_byte_1', pd.Grouper(key='timestamp', freq=freq)],sort=False)\
              .last() \
              .reset_index()     
             
                    
        elif(len(byte_req)==2):         
              df_conv= df_conv_ini.groupby(['req_byte_1', 'req_byte_2', pd.Grouper(key='timestamp', freq=freq)],sort=False) \
              .last() \
              .reset_index()     
                    
        
        elif(len(byte_req)==3):     
              df_conv= df_conv_ini.groupby(['req_byte_1', 'req_byte_2', 'req_byte_3', pd.Grouper(key='timestamp', freq=freq)], sort=False) \
              .last() \
              .reset_index()     
                    
                    
        elif(len(byte_req)==4):           
              df_conv= df_conv_ini.groupby(['req_byte_1', 'req_byte_2', 'req_byte_3','req_byte_4', pd.Grouper(key='timestamp', freq=freq)], sort=False) \
              .last() \
              .reset_index() 
    
    else:
        df_conv= df_conv_ini        
            
    return [df_conv, df_last]

    #####################Function Plot Time series######################

def plot_figures(df_conv, df_last, signal_val_plt):  

    figs_plt=[]
    for i in range(1, len(df_last.columns)+1):
          figr= plt.figure(figsize=(15, 13))
          plot1= plt.subplot(211)
          q=f"req_byte_{i}"
          plot1.plot(df_conv['timestamp'], df_conv[q], color='red')
          plt.xticks(rotation=90) 
          ax = plt.gca()
          
          start, end = ax.get_xlim() 
          if signal_val_plt=='statusLaden':
              ax.set_title('Status Laden')
          else:
              ax.set_title(f'{signal_val_plt}: Data-CCU Time Series Byte {i}')
          ax.set_ylabel('Y value')
          ax.set_xlabel('Timestamp')
          figs_plt.append(figr)
          
    return figs_plt 

    # pp.savefig(fig)
    # pp.close()
     
    #####################Function Generate PDF######################
    
 
def generate_pdf(figs_plt, file_name_input):
    
    
    dir_name= os.path.dirname(file_name_input)
    base_name= os.path.basename(file_name_input)
    file_name= file_name_input
    file_ext = base_name
    if base_name== '':
        file_ext= 'anomaly_detection_plots.pdf'
    elif not base_name.endswith('.pdf'):
        file_ext= base_name + '.pdf'
        
  
    if isinstance(Path(file_name_input),Path) and dir_name!="":
        if not os.path.exists(file_name_input):
            os.makedirs(file_name_input, mode=0o777)
        else:
            file_name = file_name_input         
          
        if not file_name_input.endswith('.pdf'):
             file_name= file_name +'/'+ file_ext
            
    else:        
        parent_path= Path(os.getcwd())
        path_name = os.path.join(str(parent_path.parent) + '/' + 'anomaly_detection')
        if not os.path.exists(path_name):
            path_name = str(parent_path.parent) + '/' + 'anomaly_detection'
            os.makedirs(path_name, mode=0o777)
        if file_name_input.endswith('.pdf'):
            file_name= path_name +  '/' + str(base_name)
        else:
            file_name= path_name + '/' + file_ext
   
   
    pp = PdfPages(file_name)
    for figr in figs_plt: 
        pp.savefig(figr)
    pp.close()
    os.startfile(file_name)   


###########Neural Work################ 

def autoencoder_model(X, activation_val):
    inputs = Input(shape=(X.shape[1], X.shape[2]))
    L1 = LSTM(16, activation= activation_val, return_sequences=True, 
              kernel_regularizer=regularizers.l2(0.00))(inputs)
    L2 = LSTM(4, activation= activation_val, return_sequences=False)(L1)
    L3 = RepeatVector(X.shape[1])(L2)
    L4 = LSTM(4, activation= activation_val, return_sequences=True)(L3)
    L5 = LSTM(16, activation= activation_val, return_sequences=True)(L4)
    output = TimeDistributed(Dense(X.shape[2]))(L5)    
    model = tf.keras.models.Model(inputs=inputs, outputs=output)
    return model
    
def anomaly_detection_fun(df_conv, df_last, signal_val_an, activation_val, threshold_val): 
    
    anomlay_figures= []
    df_analysis_ini= pd.DataFrame(data=df_conv, index=None, columns=df_conv.columns)
    df_analysis_ini = df_analysis_ini.drop(columns=['frame_id', 'vehicle_vin'])
    dfs=[]
    form=['','df_byte1','df_byte2','df_byte3','df_byte4']
    
    for i in range(1, len(df_last.columns)+1):
        vars()[form[i]] = pd.DataFrame()
        q=f"req_byte_{i}"
        vars()[form[i]]['timestamp'] = df_analysis_ini['timestamp']
        vars()[form[i]][q] = df_conv[q]
        dfs.append(vars()[form[i]])
    
    for i in range(len(dfs)):
        df_analysis_transf= dfs[i]
        train, test= np.split(dfs[i], [int(.78 *len(dfs[i]))])
        train = train.set_index('timestamp')
        test = test.set_index('timestamp')
    
        scaler = MinMaxScaler()
        X_train = scaler.fit_transform(train)
        X_test = scaler.transform(test)
        scaler_filename = "scaler_data"
        joblib.dump(scaler, scaler_filename)
        
        # reshape inputs for LSTM [samples, timesteps, features]
        X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
        #print("Training data shape:", X_train.shape)
        X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])
        #print("Test data shape:", X_test.shape)
        
        # define the autoencoder network model
        
        # create the autoencoder model
        model = autoencoder_model(X_train, activation_val)
        model.compile(optimizer='adam', loss='mae')
        model.summary()
        
        # fit the model to the data
        nb_epochs = 5              #30
        batch_size = 64              #10
        history = model.fit(X_train, X_train, epochs=nb_epochs, batch_size=batch_size,
                            validation_split=0.05).history
        
        # plot the training losses
        fig, ax = plt.subplots(figsize=(14, 6), dpi=80)
        ax.plot(history['loss'], 'b', label='Train', linewidth=2)
        ax.plot(history['val_loss'], 'r', label='Validation', linewidth=2)
        ax.set_title(f'{signal_val_an}: Byte{i+1} Model loss: {activation_val}', fontsize=16)
        ax.set_ylabel('Loss (mae)')
        ax.set_xlabel('Epoch')
        ax.legend(loc='upper right')
        plt.show()
        anomlay_figures.append(fig)

        
        #####new block######  #######lestercardoz code
        
        pred_train = model.predict(X_train)
        pred_train = pred_train.reshape(pred_train.shape[0],pred_train.shape[2])
        pred_train = pd.DataFrame(pred_train, columns=train.columns)
        pred_train.index = train.index
        
        scored_train = pd.DataFrame(index=train.index)
        Xtrain = X_train.reshape(X_train.shape[0],X_train.shape[2])
        scored_train['Loss_mae'] = np.mean(np.abs(pred_train-Xtrain), axis = 1)
        plt.figure(figsize=(16,9), dpi=80)
        g2 = sns.distplot(scored_train['Loss_mae'], bins = 50, kde= True, color = 'blue');
        plt.title(f'{signal_val_an}: Byte{i+1}- Loss Distribution Train Data')
        plt.xlabel('Loss (MAE)')
        plt.show()
        fig2 = g2.get_figure()
        anomlay_figures.append(fig2)
        
        user_TH= threshold_val[signal_val_an]
        
        if user_TH!='':
            TH = float(threshold_val[signal_val_an])
        else:
            TH= np.mean(scored_train['Loss_mae']) + 5 * np.std(scored_train['Loss_mae'])
        
        print(TH)
        
        scored_train = pd.DataFrame(index=train.index)
        scored_train['Loss_mae'] = np.mean(np.abs(pred_train-Xtrain), axis = 1)
        scored_train['Threshold'] = TH
        scored_train['Anomaly'] = scored_train['Loss_mae'] > scored_train['Threshold']
        
        #scored_train.plot(logy=True,  figsize=(16,9), ylim=[1e-2,1e2], color=['blue','red'])
        
        
        scored_train['Loss_mae'].mean()
        
        # scored_train.plot(logy=True,  figsize = (16,4), xlim =[0,len(scored_train)])
        # plt.xlabel('Data points')
        # plt.ylabel('Loss (MAE)')
            
        #scored_train
        
        anomalies = scored_train[scored_train['Anomaly'] == True]
        print(anomalies)
        print(anomalies.shape)
        
        
        f, (ax1) = plt.subplots(figsize=(16, 4))
        ax1.plot(scored_train.index, scored_train.Loss_mae, label='Loss(MAE)')
        ax1.plot(scored_train.index, scored_train.Threshold, label='Threshold')
        g3 = sns.scatterplot(x=anomalies.index , y=anomalies.Loss_mae, label='anomaly', color='red')
        #g.set(xlim = (0, len(scored_train.index)))
        plt.title(f'{signal_val_an}: Byte{i+1} Anomalies- Train Data')
        plt.xlabel('Timestamp')
        plt.ylabel('Loss (MAE)')
        plt.legend()
        plt.show()
        fig3 = g3.get_figure()
        anomlay_figures.append(fig3)

         
        ####test set
        
        score = model.evaluate(X_test,X_test)
        score
        
        pred_test = model.predict(X_test)
        pred_test = pred_test.reshape(pred_test.shape[0],pred_test.shape[2])
        pred_test = pd.DataFrame(pred_test, columns=test.columns)
        pred_test.index = test.index
        
        scored_test = pd.DataFrame(index=test.index)
        Xtest = X_test.reshape(X_test.shape[0],X_test.shape[2])
        scored_test['Loss_mae'] = np.mean(np.abs(pred_test-Xtest), axis = 1)
        plt.figure(figsize=(16,9), dpi=80)
        g4 = sns.distplot(scored_test['Loss_mae'], bins = 50, kde= True, color = 'blue');
        plt.title(f'{signal_val_an}: Byte{i+1}- Loss Distribution Test Data')
        plt.xlabel('Loss (MAE)')
        plt.show()
        fig4 = g4.get_figure()
        anomlay_figures.append(fig4)
        
        scored_test = pd.DataFrame(index=test.index)
        scored_test['Loss_mae'] = np.mean(np.abs(pred_test-Xtest), axis = 1)
        scored_test['Threshold'] = TH
        scored_test['Anomaly'] = scored_test['Loss_mae'] > scored_test['Threshold']
        
        
        #scored_test.plot(logy=True,  figsize=(16,9), ylim=[1e-2,1e2], color=['blue','red'])
        
        #scored_test
        
        #scored_test['Loss_mae'].mean()
                
        # scored_test.plot(logy=True,  figsize = (16,4), xlim =[0,len(scored_test)])
        # plt.xlabel('Data points')
        # plt.ylabel('Loss (MAE)')
        
        
        IR_anomalies = scored_test[scored_test['Anomaly'] == True]
        print(IR_anomalies)
        print(IR_anomalies.shape)
        
        
        f, (ax2) = plt.subplots(figsize=(18, 6))
        ax2.plot(scored_test.index, scored_test.Loss_mae, label='Loss(MAE)');
        ax2.plot(scored_test.index, scored_test.Threshold, label='Threshold')
        g5 = sns.scatterplot(x=IR_anomalies.index , y=IR_anomalies.Loss_mae, label='anomaly', color='red')
        plt.title(f'{signal_val_an}: Byte{i+1} Anomalies- Test Data')
        plt.xlabel('Timestamp')
        plt.ylabel('Loss (MAE)')
        plt.legend()
        plt.show()
        fig5 = g5.get_figure()
        anomlay_figures.append(fig5)
        #g.savefig("output.png")
        #print("Accuracy: {:.2f}%".format(score[1]*100))
        
        print("Anomalies: {}".format(IR_anomalies['Anomaly'].count()))
    return anomlay_figures



if __name__ == '__main__':
    
    sig_val= main_window()
    byte_range=0
    byte_req=[]
    if  not sig_val:
        sys.exit('Input window was abruptly close')
    #print(sig_val[0])
    #print(sig_val[1])

    figs_full=[]
    
    mul_sig1= sig_val[1]['mul_signal1']
    mul_sig2= sig_val[1]['mul_signal2']
    mul_sig3= sig_val[1]['mul_signal3']
    
    activation_val= sig_val[0]["activation_val"]
    if activation_val == 'Rectified Linear Unit':
        activation_val= 'relu'
    else:
        activation_val= activation_val.lower()
        
        
    threshold_val_sig1= sig_val[0]["threshold_val"]
    
    charging_file= sig_val[0]["charging_file"]
    if charging_file:
        df_charging= read_csv(charging_file)
        df_charging_val= main(df_charging, 9, [3])
        fig_plt_chargn=plot_figures(df_charging_val[0], df_charging_val[1], 'statusLaden')
        figs_full.extend(fig_plt_chargn)
    
    if sig_val[1]["check_flag"] == False:
        filename_sig= sig_val[0]["single_signal_file"]
        if filename_sig:
            byte_range, byte_req= assigning_values(sig_val[0]["single_signal"])
            df_sig= read_csv(filename_sig)
            sig_val_mn= main(df_sig, byte_range, byte_req)
            fig_plt_sgn= plot_figures(sig_val_mn[0], sig_val_mn[1], sig_val[0]["single_signal"])
            figs_full.extend(fig_plt_sgn)
            fig_plt_sgn_an= anomaly_detection_fun(sig_val_mn[0], sig_val_mn[1], sig_val[0]["single_signal"], activation_val, threshold_val_sig1)
            figs_full.extend(fig_plt_sgn_an)
        
    else: 
        if mul_sig3=='':
            mul_signal1_file= sig_val[1]['mul_signal1_file']
            mul_signal2_file= sig_val[1]['mul_signal2_file']
            
            threshold_val_mul= sig_val[1]["threshold_val"]
            
            if mul_signal1_file and mul_signal2_file:
                byte_range1, byte_req1= assigning_values(sig_val[1]["mul_signal1"])
                df_sig_mul1= read_csv(mul_signal1_file)
                df_values1= main(df_sig_mul1, byte_range1, byte_req1)
                fig_plt1= plot_figures(df_values1[0], df_values1[1], sig_val[1]["mul_signal1"])
                figs_full.extend(fig_plt1)
                figs_an1= anomaly_detection_fun(df_values1[0], df_values1[1], sig_val[1]["mul_signal1"], activation_val, threshold_val_mul)
                figs_full.extend(figs_an1)
                
                byte_range2, byte_req2= assigning_values(sig_val[1]["mul_signal2"])
                df_sig_mul2= read_csv(mul_signal2_file)
                df_values2=main(df_sig_mul2, byte_range2, byte_req2)
                fig_plt2=plot_figures(df_values2[0], df_values2[1], sig_val[1]["mul_signal2"])
                figs_full.extend(fig_plt2)
                figs_an2=anomaly_detection_fun(df_values2[0], df_values2[1], sig_val[1]["mul_signal2"], activation_val, threshold_val_mul)
                figs_full.extend(figs_an2)
    
        else:
            mul_signal1_file= sig_val[1]['mul_signal1_file']
            mul_signal2_file= sig_val[1]['mul_signal2_file']
            mul_signal3_file= sig_val[1]['mul_signal3_file']
            
            if mul_signal1_file and mul_signal2_file and mul_signal3_file:
                byte_range1, byte_req1= assigning_values(sig_val[1]["mul_signal1"])
                df_sig_mul1= read_csv(mul_signal1_file)
                df_sig_values_mul1= main(df_sig_mul1, byte_range1, byte_req1)
                fig_mul_plt1=plot_figures(df_sig_values_mul1[0], df_sig_values_mul1[1], sig_val[1]["mul_signal1"])
                figs_full.extend(fig_mul_plt1)
                fig_mul_plt_an1=anomaly_detection_fun(df_sig_values_mul1[0], df_sig_values_mul1[1], sig_val[1]["mul_signal1"], activation_val, threshold_val_mul)
                figs_full.extend(fig_mul_plt_an1)
                
                byte_range2, byte_req2= assigning_values(sig_val[1]["mul_signal2"])
                df_sig_mul2= read_csv(mul_signal2_file)
                df_sig_values_mul2= main(df_sig_mul2, byte_range2, byte_req2)
                fig_mul_plt2=plot_figures(df_sig_values_mul2[0], df_sig_values_mul2[1], sig_val[1]["mul_signal2"])
                figs_full.extend(fig_mul_plt2)
                fig_mul_plt_an2= anomaly_detection_fun(df_sig_values_mul2[0], df_sig_values_mul2[1], sig_val[1]["mul_signal2"], activation_val, threshold_val_mul)
                figs_full.extend(fig_mul_plt_an2)
                
                byte_range3, byte_req3= assigning_values(sig_val[1]["mul_signal3"])
                df_sig_mul3= read_csv(mul_signal3_file)
                df_sig_values_mul3=main(df_sig_mul3, byte_range3, byte_req3)
                fig_mul_plt3=plot_figures(df_sig_values_mul3[0], df_sig_values_mul3[1], sig_val[1]["mul_signal3"])
                figs_full.extend(fig_mul_plt3)
                fig_mul_plt_an3=anomaly_detection_fun(df_sig_values_mul3[0], df_sig_values_mul3[1], sig_val[1]["mul_signal3"], activation_val, threshold_val_mul)
                figs_full.extend(fig_mul_plt_an3)
                
    generate_pdf(figs_full, sig_val[0]["output_file"]) 
       
        
    

       
#pdfReader = PdfFileReader(open(files, 'rb'))            

    # print(byte_range)
    # print(byte_req)

        

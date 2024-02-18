import pandas as pd
import numpy as np
import os
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from ._BgoVAE import svae
from tensorflow.keras.models import load_model
from ._VSGNN import vsg
from ._BgoVAE.svae import SelfAttentionBlock

def _StandardScaler(data):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    _mean = scaler.mean_
    _variance = scaler.var_
    return scaled_data, _mean,_variance

def _InvScaler(data,mean,var):
    return data * np.sqrt(var) + mean
    

def train(data_file, input_dim, y_dim, latent_dim, epochs=500, batch_size=32,patience=20):
    """
    ================================================================
    DVSNet : Dynamic Virtual Space generation neural Network.
    Author: Bin CAO <binjacobcao@gmail.com> 
    Guangzhou Municipal Key Laboratory of Materials Informatics, Advanced Materials Thrust,
    Hong Kong University of Science and Technology (Guangzhou), Guangzhou 511400, Guangdong, China
    ================================================================
    Please feel free to open issues in the Github :
    https://github.com/Bin-Cao/Bgolearn
    or 
    contact Mr.Bin Cao (bcao686@connect.hkust-gz.edu.cn)
    in case of any problems/comments/suggestions in using the code. 
    ==================================================================
    DVSNet is an associated neural network for the Bgolearn project.
    Thank you for choosing Bgolearn for material design. 
    ================================================================
    FUNCTION train :

    :param data_file: the file location of the training data

    :param input_dim: the dimension of features to train

    :param y_dim: the dimension of targets to train

    :param latent_dim : the dimension of latent variables in encoding space

    :param epochs : the number of epochs to train

    :param batch_size : the batch size of the training data 

    :param patience : the number of epochs to wait before stopping the training process once 
        the monitored metric has stopped improving. 
    
    example :  

    data_file = './dataset/traindata.csv'
    input_dim = 4 
    y_dim = 1
    latent_dim = 15 
    epochs = 500
    batch_size = 16 
    patience = 20
    DVSNet.train(data_file, input_dim, y_dim, latent_dim, epochs=500, batch_size=32,patience=20)

    """
    os.makedirs('DSVNetparams', exist_ok=True)
    # Load your data
    data = pd.read_csv(data_file)
    # Preprocess the data
    scaled_data, _mean,_variance = _StandardScaler(data)
    np.savez('./DSVNetparams/mean_and_variance.npz', mean=_mean, variance=_variance)

    # Split the data into training and testing sets
    train, test = train_test_split(scaled_data, test_size=0.2, random_state=42)

    _svae = svae.build_svae(input_dim, y_dim, latent_dim,)

    # Define callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=patience, verbose=1, mode='min')
    model_checkpoint = ModelCheckpoint('./DSVNetparams/best_model.h5', monitor='val_loss', save_best_only=True, verbose=1, mode='min')

    history = _svae.fit([train[:,:-y_dim], train[:,-y_dim:]], 
                  epochs=epochs, 
                  batch_size=batch_size, 
                  validation_data=([test[:,:-y_dim], test[:,-y_dim:]], None),
                  callbacks=[early_stopping, model_checkpoint])


def round_step(arr,step_list):
    arr = arr.numpy()
    for i, step in enumerate(step_list):
        arr[:, i] = np.round(arr[:, i] / step) * step
    return arr
    
def generator(data_file,input_dim, y_dim, latent_dim,step_list,gen_num=100):
    """
    ================================================================
    DVSNet : Dynamic Virtual Space generation neural Network.
    Author: Bin CAO <binjacobcao@gmail.com> 
    Guangzhou Municipal Key Laboratory of Materials Informatics, Advanced Materials Thrust,
    Hong Kong University of Science and Technology (Guangzhou), Guangzhou 511400, Guangdong, China
    ================================================================
    Please feel free to open issues in the Github :
    https://github.com/Bin-Cao/Bgolearn
    or 
    contact Mr.Bin Cao (bcao686@connect.hkust-gz.edu.cn)
    in case of any problems/comments/suggestions in using the code. 
    ==================================================================
    DVSNet is an associated neural network for the Bgolearn project.
    Thank you for choosing Bgolearn for material design. 
    ================================================================
    FUNCTION generator :

    :param data_file: the file location of the desired data

    :param input_dim: the dimension of features to genreation

    :param y_dim: the dimension of targets to genreation

    :param latent_dim : the dimension of latent variables in encoding space

    :param gen_num : for each desired datum, gen_num visual samples will be generated.

    :param step_list : the design step of each feature 

    example :  

    data_file = './dataset/desireddata.csv'
    input_dim = 4 
    y_dim = 1
    latent_dim = 15 
    step_list = [0.5,5,50,1]
    gen_num = 100
    DVSNet.generator(data_file, input_dim, y_dim, latent_dim,step_list,gen_num,)
    """
    os.makedirs('BgolearnData', exist_ok=True)

    # load the virtual samples generator  
    vsg_model = vsg.build_vsg(input_dim, y_dim, latent_dim,gen_num)
    
    # upload the model weights 
    pretrain_weights ='./DSVNetparams/best_model.h5'  
    vsg_model.load_weights(pretrain_weights, by_name=True,)


    # Freeze parameters
    for layer in vsg_model.layers:
        layer.trainable = False

    # Load your data
    data = pd.read_csv(data_file)
    cal_name = data.columns[:-y_dim]
    data = np.array(data)

    loaded_data = np.load('./DSVNetparams/mean_and_variance.npz')
    mean_loaded = loaded_data['mean']
    try:
        variance_loaded = loaded_data['variance']
    except Exception as e: 
        print('Error loading! The configuration of the generator net may have been changed.')  
        print('Please make sure that the dimensions of the data are consistent with the training parameters.')
        print('Error Details:', e)

    data = (data - mean_loaded) / np.sqrt(variance_loaded)

    generated_data = []
    for sample in data:
        _z = vsg_model.predict([sample[:-y_dim].reshape(1, -1), np.array([sample[-y_dim:]])])

        generated_data.append(_z * np.sqrt(variance_loaded[:-y_dim]) + mean_loaded[:-y_dim])


    arr = tf.reshape(generated_data, (len(data)*gen_num, input_dim))
    generated_data = pd.DataFrame(round_step(arr,step_list)  ,columns=cal_name)
    generated_data.to_csv('./BgolearnData/vs_data.csv',index=False)

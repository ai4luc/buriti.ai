"""
Software Open Source
©Copyright Mateus de Souza Miranda, 2023
mateus.miranda@inpe.br; mateusmirandaa2@hotmail.com
National Institute for Space Research (INPE)
São José dos Campos, São Paulo, Brazil

Version 4:  January, 2023
"""

# -------- Packs --------
# Data
import os
import numpy as np
from glob import glob
import skimage.io as skio

# Metrics
from sklearn.metrics import f1_score, precision_score, confusion_matrix, accuracy_score

# Graphs
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# -------- Pixel-based assessment --------
# Set up
classes_cerradata = ['impervious_surface', 'building', 'low_vegetation', 'tree', 'car', 'background']

lista_class = {'impervious_surface':0, 'building':1, 'low_vegetation':2, 'tree':3, 'car':4, 'background':5}

lista_class_r = {value: key for key, value in zip(lista_class.keys(), lista_class.values())}


# Metricas
def compute_iou(label, pred):
    unique_labels = np.unique(label)
    num_unique_labels = len(unique_labels)
    iou = {}

    for index, val in enumerate(unique_labels):
        pred_i = pred == val
        label_i = label == val

        I = float((label_i & pred_i).sum())
        U = float((label_i | pred_i).sum())
        iou[lista_class_r[val]] = (I / U)

    return iou


def compute_mean_iou(pred, label):
    unique_labels = np.unique(label)
    num_unique_labels = len(unique_labels);
    iou = {}  # adicionei - Marcos

    I = np.zeros(num_unique_labels)
    U = np.zeros(num_unique_labels)

    for index, val in enumerate(unique_labels):
        pred_i = pred == val
        label_i = label == val
        print(pred_i)
        print(label_i)
        print(np.logical_and(label_i, pred_i))
        print(np.sum(np.logical_and(label_i, pred_i)))

        I[index] = float(np.sum(np.logical_and(label_i, pred_i)))
        U[index] = float(np.sum(np.logical_or(label_i, pred_i)))
        iou[lista_class_r[val]] = (I[index] / U[index])  # adicionei - Marcos

    mean_iou = np.mean(I / U)
    return mean_iou, iou


def compute_mean_iou_weighted(label, pred):
    unique_labels = np.unique(label)
    num_unique_labels = len(unique_labels)
    iou = {}
    mIoU_weighted = 0.0

    for index, val in enumerate(unique_labels):
        pred_i = pred == val
        label_i = label == val

        I = float((label_i & pred_i).sum())
        U = float((label_i | pred_i).sum())
        iou[lista_class_r[val]] = (I / U)

        mIoU_weighted += (iou[lista_class_r[val]] * (label_i).sum())

    mIoU_weighted = mIoU_weighted / label.ravel().shape[0]

    return iou, mIoU_weighted


# Data loading
def load_image(path):
    # List
    patch = list()
    name_file = []
    # Path of the Images
    list_file = glob(path)
    # Sorting name file
    list_file.sort()

    # Loop
    for sample in list_file:
        # name of file
        name_file.append(os.path.basename(sample))

        # Read Image
        raster = skio.imread(sample)
        patch.append(raster)

    return patch, name_file


# Paths
path_true = '../dataset/Potsdam_split/seg/'
path_pred = '../models/deeplabv3plus/outputs_150epochs/'
print('Dados lidos')
y_true, name_ytrue = load_image(path_true + '*.png')
y_pred, name_ypred = load_image(path_pred + '*.png')

y_pred = np.array(y_pred).astype('int32')
y_true = np.array(y_true).astype('int32')
print(np.unique(y_pred))
print(y_true.shape)
print(y_pred.shape)

# Metrics
"""
# 1. IoU and mIoU
iou, mean_iou_weighted = compute_mean_iou_weighted(y_true, y_pred)
print('IoU: ', iou)
print('mIoUw: ', mean_iou_weighted)
"""

# 2. F1-score
f1score = f1_score(y_true.flatten(), y_pred.flatten(), average='weighted')
print('F1-score:', float(f1score))

# 3. Accuracy
acc = accuracy_score(y_true.flatten(), y_pred.flatten())
print('Accuracy:', acc)

# 4. Precision
#precision = precision_score(y_true.flatten(), y_pred.flatten(), average='weighted')
#sprint('Precision:', float(precision))
"""
# 5. Confusion Matrix
confusionMatrix = confusion_matrix(y_true.flatten(), y_pred.flatten())
print(confusionMatrix)

# Plotar a matriz de confusão
plt.figure(figsize=(8, 6))
plt.imshow(confusionMatrix, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Matriz de Confusão')
plt.colorbar()
classes = [0, 1, 2, 3, 4, 5]  # Substitua pelas classes reais do seu problema
tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, classes, rotation=45)
plt.yticks(tick_marks, classes)
plt.ylabel('Rótulos Reais')
plt.xlabel('Rótulos Previstos')

# Adicione os valores da matriz nos quadrados
thresh = confusionMatrix.max() / 2.
for i in range(confusionMatrix.shape[0]):
    for j in range(confusionMatrix.shape[1]):
        plt.text(j, i, format(confusionMatrix[i, j], 'd'),
                 ha="center", va="center",
                 color="white" if confusionMatrix[i, j] > thresh else "black")

plt.tight_layout()
plt.show()
"""

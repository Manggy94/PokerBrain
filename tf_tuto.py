import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import sklearn.preprocessing as prep
import sklearn.model_selection as select
import pandas as pd
import sys

fashion_mnist=tf.keras.datasets.fashion_mnist
(images, targets), (_,_)=fashion_mnist.load_data()
images=images[:10000]
targets=targets[:10000]

#flatten data
images=images.reshape(-1, 784)
images=images.astype(float)
#print(images.shape)
#Normalizationn of data
scaler=prep.StandardScaler()
images=scaler.fit_transform(images)

img_train, img_test, targets_train, targets_test=select.train_test_split(images, targets, test_size=0.2, random_state=1)
print(img_train.shape, targets_train.shape)
print(img_test.shape, targets_test.shape)

#exit()


##target_names=["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]
#i=np.random.randint(0,10000)
#plt.imshow(images[i], cmap="binary")
#plt.title(target_names[targets[i]])
#plt.show()

#Create the model

model=tf.keras.models.Sequential()
#Flatten input
#model.add(tf.keras.layers.Flatten(input_shape=[28,28]))
#Add layers
model.add(tf.keras.Input(shape=(784,)))
model.add(tf.keras.layers.Dense(256, activation="relu"))
model.add(tf.keras.layers.Dense(128, activation="relu"))
model.add(tf.keras.layers.Dense(10, activation="softmax"))

#print("Shape of img",  images[0:1].shape)
#model_output=model.predict(images[0:1])
#print(model_output, targets[0:1])
model.summary()

#Compile the model
model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="sgd",
    metrics=["accuracy"]
)
#Train the model

history=model.fit(img_train, targets_train, epochs=20, validation_split=0.2)
print(history.history)
#exit()

loss_curve=history.history["loss"]
acc_curve=history.history["accuracy"]
loss_val_curve=history.history["val_loss"]
acc_val_curve=history.history["val_accuracy"]
fig,axs=plt.subplots(1,2)

axs[0].plot(loss_curve, color='tab:blue', label="Training Set")
axs[0].set_title(" Loss")
axs[0].set_xlabel("Epochs")
axs[1].plot(acc_curve, color='tab:blue', label="Training Set")
axs[1].set_title("Accuracy")
axs[1].set_xlabel("Epochs")
axs[0].plot(loss_val_curve, color='tab:green', label="Test Set")
#axs[1,0].set_title("Validation Set Loss")
#axs[1,0].set_xlabel("Epochs")
axs[1].plot(acc_val_curve, color='tab:green', label="Test Set")
#axs[1,1].set_title("Validation Set Accuracy")
#axs[1,1].set_xlabel("Epochs")
plt.show()
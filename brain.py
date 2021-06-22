import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import sklearn.preprocessing as prep
import sklearn.model_selection as select
import converter as conv
import Guesser.models as guess
#import model as md
# import pandas as pd
# import sys

range_loss = guess.range_loss

features, targets = conv.vectorize("history")

print(features.shape, targets.shape)

# flatten data
# features=features.reshape(-1, 784)
# images=images.astype(float)
# print(features.shape)
# Normalizationn of data
scaler = prep.StandardScaler()
features = scaler.fit_transform(features)

train_set, test_set, train_tgts, test_tgts = select.train_test_split(features, targets, test_size=0.2, random_state=1)
print(train_set.shape, train_tgts.shape)
print(test_set.shape, test_tgts.shape)

# exit()
# Create the model

model = tf.keras.models.Sequential()
# Flatten input
# model.add(tf.keras.layers.Flatten(input_shape=[28,28]))
# Add layers
model.add(tf.keras.Input(shape=(447,)))
model.add(tf.keras.layers.Dense(256, activation="relu"))
model.add(tf.keras.layers.Dense(128, activation="relu"))
model.add(tf.keras.layers.Dense(64, activation="relu"))
model.add(tf.keras.layers.Dense(32, activation="relu"))
model.add(tf.keras.layers.Dense(1326, activation="softmax"))

# print("Shape of img",  images[0:1].shape)
# print(model_output, targets[0:1])
model.summary()

# Compile the model
model.compile(
    loss="categorical_crossentropy",
    optimizer="sgd",
    metrics=["categorical_accuracy", tf.keras.metrics.top_k_categorical_accuracy],
    run_eagerly=True
)

# Train the model

history = model.fit(train_set, train_tgts, epochs=120, validation_split=0.2)
print(history.history)


loss_curve = history.history["loss"]
acc_curve = history.history["categorical_accuracy"]
top_k_curve = history.history['top_k_categorical_accuracy']
loss_val_curve = history.history["val_loss"]
acc_val_curve = history.history["val_categorical_accuracy"]
top_k_val_curve = history.history['val_top_k_categorical_accuracy']
fig, axs = plt.subplots(1,2)

axs[0].plot(loss_curve, color='tab:blue', label="Training Loss")
axs[0].plot(loss_val_curve, color='tab:red', label="Validation Loss")
axs[0].set_title("Loss")
axs[0].set_xlabel("Epochs")

axs[1].plot(acc_curve, color='tab:blue', label="Training Accuracy")
axs[1].set_title("Accuracy")
axs[1].set_xlabel("Epochs")
axs[1].plot(acc_val_curve, color='tab:red', label="Validation Accuracy")
axs[1].plot(top_k_curve, color='tab:green', label="Training Top-5")
axs[1].plot(top_k_val_curve, color='tab:orange', label="Test Top-5")
plt.legend(loc='upper left')
# axs[1,1].set_title("Validation Set Accuracy")
# axs[1,1].set_xlabel("Epochs")
plt.show()


print(" Evaluation du test set")
results = model.evaluate(test_set, test_tgts, batch_size=20)
print("test loss, test acc, top-5-accuracy", results)
accuracy, top5acc = results[1], results[2]
if accuracy > 0.75 and top5acc > 0.9:
    model.save("Brains/Brain1")


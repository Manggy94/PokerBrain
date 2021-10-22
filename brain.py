import matplotlib.pyplot as plt
import tensorflow as tf
from preprocessor import Preprocessor
import sklearn.model_selection as select
from API.timer import Timer

t1 = Timer()
t1.start()
t2 = Timer()
t2.start()
print("Data Preparation")
pp = Preprocessor()
X, y = pp.create_vectors(pp.conv.load_hands())
features, targets = pp.X_transformer.fit_transform(X), pp.y_transformer.fit_transform(y)
t1.stop()
print(features.shape, targets.shape)
train_set, test_set, train_tgts, test_tgts = select.train_test_split(features, targets, test_size=0.2, random_state=1)
print(train_set.shape, train_tgts.shape)
print(test_set.shape, test_tgts.shape)
print("Data is compeletely Ready")
t2.stop()

# exit()
# Create the model
print("Model Creation and Training")
t3 = Timer()
t3.start()
model = tf.keras.models.Sequential()
# Flatten input
# model.add(tf.keras.layers.Flatten(input_shape=[28,28]))
# Add layers
model.add(tf.keras.Input(shape=(features.shape[1],)))
model.add(tf.keras.layers.Dense(256, activation="relu"))
model.add(tf.keras.layers.Dense(128, activation="relu"))
model.add(tf.keras.layers.Dense(64, activation="relu"))
model.add(tf.keras.layers.Dense(32, activation="relu"))
model.add(tf.keras.layers.Dense(targets.shape[1], activation="softmax"))

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

history = model.fit(train_set, train_tgts, epochs=50, validation_split=0.2)
print(history.history)
t3.stop()
print("Model is ready")


loss_curve = history.history["loss"]
acc_curve = history.history["categorical_accuracy"]
top_k_curve = history.history['top_k_categorical_accuracy']
loss_val_curve = history.history["val_loss"]
acc_val_curve = history.history["val_categorical_accuracy"]
top_k_val_curve = history.history['val_top_k_categorical_accuracy']
fig, axs = plt.subplots(1, 2)

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
exit()
if accuracy > 0.75 and top5acc > 0.9:
    model.save("Brains/Brain1")

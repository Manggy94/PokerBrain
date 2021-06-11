import tensorflow as tf
from tensorflow import keras
import keras.backend as K


class RangeModel(keras.Model):
    def train_step(self, data):
        # Unpack the data. Its structure depends on your model and
        # on what you pass to `fit()`.
        x, y = data

        with tf.GradientTape() as tape:
            y_pred = self(x, training=True)  # Forward pass
            # Compute the loss value
            # (the loss function is configured in `compile()`)
            loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)

        # Compute gradients
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)
        # Update weights
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        # Update metrics (includes the metric that tracks the loss)
        self.compiled_metrics.update_state(y, y_pred)
        # Return a dict mapping metric names to current value
        return {m.name: m.result() for m in self.metrics}

class RangeLoss(keras.losses.Loss):
    pass


@tf.function
def range_loss(y_true, y_pred):
    m=K.sum(y_pred, axis=1)
    n=y_true.shape[1]
    alpha=1
    beta=1
    err_log = -K.sum(y_true * K.log(y_pred) + (1 - y_true) * K.log(1 - y_pred), axis=1)
    err_prec = -K.log(1 - m / n )
    print(err_log, err_prec)
    err = alpha*err_log + beta*err_prec
    print(err)
    return err

@tf.function
def range_loss2(y_true, y_pred):
    err_accuracy=-K.log(tf.keras.metrics.top_k_categorical_accuracy(y_true=y_true, y_pred=y_pred, k=5))
    return err_accuracy


def range_size(prediction):
    p = 0.8
    combo_range = 1 * (prediction > p)
    return K.sum(combo_range, axis=1)



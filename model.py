import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

import matplotlib.pyplot as plt

# -----------------------------
# data
# -----------------------------

file_path = 'data.json'
with open(file_path, 'r') as file: data = json.load(file)

keys = list(data.keys())
# Convert keys into a 2D NumPy array. a key example is '0100211200101020'
X = np.array([[int(char) for char in key] for key in keys])

# Normalize the data by replacing all 2s with -1s
X[X == 2] = -1

# Extract values into a parameter `y`
values = np.array(list(data.values()))
y = values[:,0]

print("X:")
print(X.shape)
print("Y:")
print(y.shape)

# -----------------------------
# Split data into Train  / Test
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # It's not necessary to normalize the data since it's already normalized (-1 and 1)
# # Normalize the data using MinMaxScaler
# scaler = MinMaxScaler()
# scaler.fit(X_train) # Fit scaler only on training data
# X_train_normalized = scaler.transform(X_train)
# X_test_normalized = scaler.transform(X_test)

# -----------------------------
# Network Architecture
# -----------------------------

# Build the model
model = Sequential([
    Dense(64, activation='relu', input_shape=(9,)),  # Input layer
    Dropout(0.2),  # Regularization to prevent overfitting
    Dense(32, activation='relu'),  # Hidden layer
    Dropout(0.2),  # Regularization to prevent overfitting
    Dense(16, activation='relu'),  # Hidden layer
    Dense(1, activation='sigmoid')  # Output layer with sigmoid for range 0-1
])

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), # 0.001 - default learning rate for Adam
    loss='mean_squared_error',  # Loss for regression problems
    metrics=['mae'])  # Mean Absolute Error as a metric

# Define EarlyStopping callback to monitor validation loss
early_stopping = EarlyStopping(
    monitor='val_loss',        # Monitor the validation loss
    patience=5,                # Number of epochs to wait for improvement before stopping
    restore_best_weights=True   # Rollback to the best weights once stopped
)

# Train the model
history = model.fit(X_train, y_train,
    validation_split=0.2,
    epochs=100,  # Adjust based on performance
    batch_size=32,
    callbacks=[early_stopping], # Activating the early stopping mechanism
    verbose=1)

# Evaluate the model
test_loss, test_mae = model.evaluate(X_test, y_test)
print(f"Test Loss: {test_loss:.4f}, Test MAE: {test_mae:.4f}")

# Predict on new data
predictions = model.predict(X_test[:5])
print("Predictions for the first 5 rows:", predictions)

# -----------------------------
# Test parameters and calculate the quality of the model
# -----------------------------

# Print the learned weights
weights = model.get_weights()
print("Learned Weights and Bias:")
print(f"Weights: {weights[0].flatten()}, Bias: {weights[1][0]}")

# ------------------------------
# Test the model with a sample board and its rotated version
# -----------------------------

# Create a sample board: X in top-left, O in the center
board_orig = np.array([1, 0, 0, 0, -1, 0, 0, 0, 0])

# Reshape to 3x3, rotate 90 degrees, and flatten back to 9 elements
board_3x3 = board_orig.reshape(3, 3)
board_rot90 = np.rot90(board_3x3, k=1).flatten()

# Predict scores (reshape to 2D array as required by Keras)
pred_orig = model.predict(board_orig.reshape(1, -1))[0][0]
pred_rot = model.predict(board_rot90.reshape(1, -1))[0][0]

print(f"Original Board Shape: {board_orig.reshape(3, 3)}")
print(f"Rotated Board Shape: {board_rot90.reshape(3, 3)}")
print(f"Original Board Score: {pred_orig:.4f}")
print(f"Rotated Board Score: {pred_rot:.4f}")
print(f"Difference: {abs(pred_orig - pred_rot):.4f}")

# ------------------------------
# 6. Test the model with a "Good" and "Bad" board
# -----------------------------

# A "Good" board for X (X has a winning row at the top)
good_board = np.array([
     1, -1,  1,
     1,  1, -1,
    -1, -1,  0
]).reshape(1, -1)

# A "Bad" board for X (O has a winning row at the top)
bad_board = np.array([
     1,  0,  -1,
     1,  0,   0,
     0,  1,  -1
]).reshape(1, -1)

# Predict scores
pred_good = model.predict(good_board)[0][0]
pred_bad = model.predict(bad_board)[0][0]

print(f"Good Board Score (X wins): {pred_good:.4f} --> (Should be close to 1)")
print(f"Bad Board Score (O wins): {pred_bad:.4f} --> (Should be close to 0)")

# -----------------------------
# 5. Graphing Train vs Validation Loss
# -----------------------------

# Plot training and validation loss
plt.figure(figsize=(12, 6))

# Loss
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# MAE
plt.subplot(1, 2, 2)
plt.plot(history.history['mae'], label='Training MAE')
plt.plot(history.history['val_mae'], label='Validation MAE')
plt.title('Training and Validation MAE')
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error')
plt.legend()

plt.tight_layout()
plt.show()

# # Save the model to a file
# model.save("model.h5")
# print("Model saved successfully.")

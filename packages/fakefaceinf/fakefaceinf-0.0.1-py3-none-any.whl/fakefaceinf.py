import shutil
import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

def predict_and_process_image(input_img):
    # Load your trained model
    model = tf.keras.models.load_model('models\\fakefacedetect')  # Replace 'your_model_path' with the actual path to your trained model.

    img_height = 150
    img_width = 150

    # Load and preprocess the input image
    img = image.load_img(input_img, target_size=(img_height, img_width))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)  # Add an extra dimension to simulate a batch of one image
    img = img / 255.0  # Normalize the pixel values if your model expects it

    # Make predictions
    predictions = model.predict(img)

    # Get the predicted class
    predicted_class_index = np.argmax(predictions)
    predicted_class = ['fake', 'real'][predicted_class_index]

    # Display the predicted class
    return predicted_class  # Face is fake

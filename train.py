import os
import multiprocessing
from ultralytics import YOLO


def train_model():
    model = YOLO('yolov8n.pt')  # Example, replace with your model initialization
    results = model.train(data="config.yaml", epochs=100)  # Train the model
    return results


if __name__ == '__main__':
    # multiprocessing.freeze_support()  # Optional, useful for frozen executables
    train_model()


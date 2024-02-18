import os
import argparse
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from sklearn.model_selection import train_test_split

import soundfile as sf

try:
    # importing within package
    from models.ReverbClassifier.data import NUM_CLASSES
    from models.ReverbClassifier import ReverbClassifierNetwork

except ImportError:
    # executing this module
    from .data import NUM_CLASSES
    from .ReverbClassifierNetwork import ReverbClassifierNetwork


def train_model(path_to_data, output_directory='.'):

    data = np.load(path_to_data, allow_pickle=True)
    """Prepare dataset"""

    # check balance of data
    data_count = list()
    data_by_classification = [None] * NUM_CLASSES
    for cls in range(NUM_CLASSES):
        data_by_classification[cls] = list()
        for datum in data:
            if datum["class"] == cls:
                data_by_classification[cls].append(datum["features"])
        data_by_classification[cls] = torch.cat(data_by_classification[cls])

    data_count = [cls.shape[0] for cls in data_by_classification]
    min_samples = min(data_count)

    for cls, _ in enumerate(data_by_classification):
        data_by_classification[cls] = data_by_classification[cls][:min_samples, :]

    # unroll data
    x = list()
    y = list()

    for cls, data in enumerate(data_by_classification):
        x.append(data)
        y.append([cls] * data.shape[0])

    x = torch.cat(x)
    y = F.one_hot(torch.tensor([y for ys in y for y in ys])).type(torch.FloatTensor)

    # split dataset
    x_train, x_test, y_train, y_test = train_test_split(x, y)
    """Training"""
    net = ReverbClassifierNetwork()

    ## Optimizer
    import torch.optim as optim

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.0001, momentum=0.9)

    ## Training
    num_epochs = 10
    batch_size = 100

    for epoch in range(num_epochs):  # loop over the dataset multiple times
        running_loss = 0.0

        print(f"epoch {epoch}:")
        for i in range(epoch * batch_size, (epoch + 1) * batch_size):
            # get the inputs; data is a list of [inputs, labels]
            # inputs, labels = data

            inputs = x_train[i:i + batch_size]
            inputs_labels = y_train[i:i + batch_size]

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, inputs_labels)

            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss:.3f}')

    print('Finished Training')

    # Test
    total = 0
    correct = 0
    with torch.no_grad():
        total = y_test.size(0)
        for i in range(0, x_test.size()[0], batch_size):
            outputs = net(x_test[i:i + batch_size])
            _, predictions = torch.max(outputs, 1)
            _, oracle = torch.max(y_test[i:i + batch_size], 1)
            correct += (predictions == oracle).sum().item()

    print(f"accuracy = {correct/total}")
    print(f"correct = {correct} \t total={total}")

    now = datetime.now()
    torch.save(
        net.state_dict(),
        os.path.join(output_directory,
                     f"ReverbClassifierNetwork_{now.strftime('%Y%m%d%H%M%S')}.pt"))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="path to data")
    parser.add_argument("--output", '-o', help="where to save data")
    args, _ = parser.parse_known_args()

    assert os.path.splitext(
        args.data)[-1] == '.npy', "--data must be a numpy binary (.npy)"
    assert os.path.isdir(args.output), "--output must be a directory"

    train_model(path_to_data=args.data, output_directory=args.output)


# oneat

[![License BSD-3](https://img.shields.io/pypi/l/oneat.svg?color=green)](https://github.com/Kapoorlabs-CAPED/caped-ai-oneat/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/oneat.svg?color=green)](https://pypi.org/project/oneat)
[![Python Version](https://img.shields.io/pypi/pyversions/oneat.svg?color=green)](https://python.org)
[![tests](https://github.com/Kapoorlabs-CAPED/oneat/workflows/tests/badge.svg)](https://github.com/Kapoorlabs-CAPED/caped-ai-oneat/actions)
[![codecov](https://codecov.io/gh/Kapoorlabs-CAPED/oneat/branch/main/graph/badge.svg)](https://codecov.io/gh/Kapoorlabs-CAPED/caped-ai-oneat)


Action classification for TZYX shaped images, Static classification for TYX shaped images

----------------------------------

This [caped] package was generated with [Cookiecutter] using [@caped]'s [cookiecutter-template] template.



## Installation

You can install `oneat` via [pip]:

    pip install oneat



To install latest development version :

    pip install git+https://github.com/Kapoorlabs-CAPED/caped-ai-oneat.git

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"oneat" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[pip]: https://pypi.org/project/pip/
[caped]: https://github.com/Kapoorlabs-CAPED
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@caped]: https://github.com/Kapoorlabs-CAPED
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[cookiecutter-template]: https://github.com/Kapoorlabs-CAPED/cookiecutter-template

[file an issue]: https://github.com/Kapoorlabs-CAPED/caped-ai-oneat/issues

[tox]: https://tox.readthedocs.io/en/latest/

## Algorithm and Code for finding mitotic cells in TZYX datasets

### Program structure

We use hydra library to separate the parameters of the code from the actual file that contains the runnable code. We do so to minimize the interaction with the actual script/file/interactive code where the users do not have to change any lines to specify the paths/filenames/parameters. The [configuration file to modify the parameters](https://github.com/Kapoorlabs-CAPED/Mari_Scripts_Server/blob/main/conf/config_oneat.yaml).

The params_train contains the training parameters for the hyperparameters of the network, these parameters are set once and for all and are not learned during the training process, hence the name hyperparameters.

The params_predict contains the parameters needed for model prediction such as the number of tiles, event threshold and confidence to veto the events below the threshold.

The trainclass contains the training class used by oneat and is input as a string. For VollNet (Resnet based) the training class is NEATVollNet, for DenseVollNet (Densenet based) the training class is DenseVollNet.

The defaults provides the filename and the paths, depending on where the data is you only have to select the path file which is supplied for local paths/ovh server paths/aws paths. This maybe a bit of gymnastics in the beginning but once the paths, files are set only parameters need to be changed during regular usage of the scripts and interactive programs.

### The training data

The training data for 3D + time dataset was made by clicking on the location in ZYX of the mitotic (blue points layer) and non-mitotic cell (red points layer) using an interactive [Napari widget](https://github.com/Kapoorlabs-CAPED/Mari_Scripts_Server/blob/main/volume_click_maker.py).

We also have the segmentation image for the raw data that we use to create the clicks and we use the segmentation labels at the click location to refine the location of the clicked cell, get it's height, width and depth that we use to create the training label.

Using a [custom training data creating script](https://github.com/Kapoorlabs-CAPED/Mari_Scripts_Server/blob/main/create_volumetric_training_patches.py) The training data consists of 1 timeframe before and after the division/mitosis splitting of the cell, 4 Z planes before and 4 Z planes after the click Z location and 32 pixels in XY around the click location in X and Y. In this fashion the non-mitotic and mitotic cells are always in the center, spatially and temporally making the task of learning easier. The shape of the training data TZYX hence is (3,8,64,64) and the training label consists of class label + 0.5,0.5,0.5,0.5,Height,Width,Depth,confidence. The 0.5 signifies the spatial and temporal centering of the cell. 

### ResNet and DenseNet based VollNet and DenseVollNet architectures

After the training data is saved as an npz file, the training can be done using a Resnet or a Densenet architecture based network. We see a better performance using    architecture. See the [Resnet implementation](https://github.com/Kapoorlabs-CAPED/caped-ai-oneat/blob/b776d98ef76fe77f17f353d045a8cf17c2f86e50/src/oneat/NEATModels/nets.py#L201-L336), see the [Densnet implementation](https://github.com/Kapoorlabs-CAPED/caped-ai-oneat/blob/b776d98ef76fe77f17f353d045a8cf17c2f86e50/src/oneat/NEATModels/nets.py#L340-L430).

We have fully convolutional implementation of both these architectures, hence the training can be done on the data of our chosen size and shape but at the prediction stage we benifit from convolutionalization of the sliding window operation where the network finds the location of the mitotic cells using the indices that the prediction function provides to map the predictions to their proper spatial and temporal locations in the input data of arbitrary size/shape.

### Program to train the model on a GPU based machine

Using [this script](https://github.com/Kapoorlabs-CAPED/Mari_Scripts_Server/blob/main/train_xenopus_oneat.py) and setting the training parameters in the configuration file we train the model with the chosen hyperparameters.

### Visualizing training loss and accuracy with Tensorboard

Oneat supports visualization of the training loss, accuracy and other training metrics using tensorboard.

Tensorboard can be started from the same directory from where you launched the training script/interactive program for training. Inside that folder you will find an **outputs** directory, inside it is a timestamped directory of logs for the tensorboard, for example the directory is named 08-21-02/ then launch tensorboard with the following command from inside the outputs directory: `tensorboard --logdir 08-21-02/`.

Tensorboard will print a localhost url to copy and paste in the browser for example `http://localhost:6007/`, clicking on the menu item of scalars shows the loss and accuracy plots for the training epochs. You can refresh the page to update the curves if it does not happen automatically.

### Model Evaluation and Prediction

Once the model has been trained, we can evaluate the performance of the model with metrics. The metrics measure the model performance on ground truth data which consists of the raw ground truth image, its corresponding segmentation image and the csv file containing the ground truth locations of the mitotic cells as TZYX columns.

For evaluating the model performance we have to run the model prediction on the ground truth raw image using its segmentation image in [this script](https://github.com/Kapoorlabs-CAPED/Mari_Scripts_Server/blob/main/predict_xenopus_oneat_volume.py). The prediction program generates a csv file containing the location of mitotic cells and also the probability, confidence scores and radius of the cell to create bounding boxes around the cell location.

Using the ground truth and the predictions csv file we compute the tru positive, false positive and false negative rate of detection using [this script](https://github.com/Kapoorlabs-CAPED/Mari_Scripts_Server/blob/main/prediction_metrics.py).

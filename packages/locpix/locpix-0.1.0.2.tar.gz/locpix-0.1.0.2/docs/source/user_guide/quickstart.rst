Quickstart
==========

Project Structure
-----------------

We assume your input SMLM data are .csv files.

This input data must first be preprocessed into a user chosen project directory, using the `Preprocess`_ script.
We strongly suggest this project directory is located outside the locpix folder.

The input and output of all further scripts will remain located inside the project directory, the input data folder
will not be accessed again!

Usage configuration
-------------------

Each script needs a configuration file (.yaml file), which should be
specified using the -c flag.

Each configuration used will be saved in the project directory.

The templates for the configuration files can be found in :ref:`templates`

Installation
------------

Prerequisites
^^^^^^^^^^^^^

You will need anaconda or miniconda or mamba.
We recommend `mamba <https://mamba.readthedocs.io/en/latest/>`_


Install
^^^^^^^

Create an environment and install via pypi

.. code-block:: console

   (base) $ conda create -n locpix-env python==3.10
   (base) $ conda activate locpix-env
   (locpix-env) $ pip install locpix



Preprocessing
-------------

Preprocess
^^^^^^^^^^

This script preprocesses the input .csv data for later use AND **must be run first**.

This script will take in .csv files, and convert them to .parquet files,
while also wrangling the data into our data format.

To run the script -i -c and -o flags should be specified

.. code-block:: console

   (locpix-env) $ preprocess -i path/to/input/data -c path/to/config/file -o path/to/project/directory

Optionally we can add:

* -s flag to check the correct files are selected before preprocessing them
* -p flag if our files are .parquet files not .csv files.

**API**
:py:mod:`locpix.scripts.preprocessing.preprocess`

Annotate
^^^^^^^^

This script allows for manual segmentation of the localisations and adding markers to the images as seeds for the watershed algorithm

To run the script -i and -c flags should be specified

.. code-block:: console

   (locpix-env) $ annotate -i path/to/project/directory -c path/to/config/file

Optionally we can add:

* -m flag to check the metadata of the project before running
* -r flag to relabel histograms, will assume some labels are already present

**API**
:py:mod:`locpix.scripts.preprocessing.annotate`

Image segmentation
------------------

Classic segmentation
^^^^^^^^^^^^^^^^^^^^

Perform classic segmentation on our localisation dataset.

To run the script without -i and -c flags should be specified

.. code-block:: console

   (locpix-env) $ classic -i path/to/project/directory -c path/to/config/file

Optionally we can add:

* -m flag to check the metadata of the project before running

**API**
:py:mod:`locpix.scripts.img_seg.classic`

Cellpose segmentation
^^^^^^^^^^^^^^^^^^^^^

.. warning::
    Need to activate extra requirements - these are big and not included in initial install.

    Note that if you have a GPU this will speed this up.

    Note we modified Cellpose to fit in with our analysis, therefore you need to install our forked repository - note below will clone the Cellpose repository to wherever you are located

    If you:

    * have a GPU

    .. code-block:: console

        (locpix-env) $ pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu117
        (locpix-env) $ git clone https://github.com/oubino/cellpose
        (locpix-env) $ cd cellpose
        (locpix-env) $ pip install .

    * don't have a GPU

    .. code-block:: console

        (locpix-env) $ pip install pytorch
        (locpix-env) $ git clone https://github.com/oubino/cellpose
        (locpix-env) $ cd cellpose
        (locpix-env) $ pip install .

Perform Cellpose segmentation on our without any retraining on your dataset run the script with -i and -c flags specified

   .. code-block:: console

      (locpix-env) $ cellpose_eval -i path/to/project/directory -c path/to/config/file

Optionally we can add:

* -m flag to check the metadata of the project before running
* -o flag to specify folder in project dir to save output (defaults to cellpose_no_train)
* -u flag to specify a user model to load in

To retrain first then evaluate we instead

   Prepare data for training

   .. code-block:: console

      (locpix-env) $ train_prep -i path/to/project/directory -c path/to/config/file

   Optionally we can add:

   * -m flag to check the metadata of the project before running

   Train cellpose

   .. code-block:: console

      (locpix-env) $ cellpose_train -i path/to/project/directory -ct path/to/config/train_file -ce path/to/config/eval_file

   Optionally we can add:

   * -m flag to check the metadata of the project before running

**API**
:py:mod:`locpix.scripts.img_seg.train_prep`
:py:mod:`locpix.scripts.img_seg.cellpose_eval`
:py:mod:`locpix.scripts.img_seg.cellpose_train`

UNET segmentation
^^^^^^^^^^^^^^^^^

Need to activate extra requirements - these are big and not included in initial install.

Note that if you have a GPU this will speed this up.

Note this is only needed if haven't done for cellpose above

If you have a GPU

.. code-block:: console

   (locpix-env) $ pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu117

If you don't have a GPU

.. code-block:: console

   (locpix-env) $ pip install pytorch

To train UNET

   .. code-block:: console

      (locpix-env) $ unet -i path/to/project/directory -c path/to/config/file

Optionally we can add:

* -m flag to check the metadata of the project before running

**API**
:py:mod:`locpix.scripts.img_seg.unet_train`

Ilastik segmentation
^^^^^^^^^^^^^^^^^^^^

Need to prepare the data for Ilastik segmentation

.. code-block:: console

   (locpix-env) $ ilastik_prep -i path/to/project/directory -c path/to/config/file

Optionally we can add:

* -m flag to check the metadata of the project before running

Then run the data through the Ilastik GUI, which needs to be installed from
`Ilastik <https://www.ilastik.org/download.html>`_  and to run it please see :ref:`ilastik-gui`.

Then convert the output of the Ilastik GUI back into our format

.. code-block:: console

   (locpix-env) $ ilastik_output -i path/to/project/directory

Optionally we can add:

* -m flag to check the metadata of the project before running

**API**
:py:mod:`locpix.scripts.img_seg.ilastik_prep`
:py:mod:`locpix.scripts.img_seg.ilastik_output`


Membrane performance
^^^^^^^^^^^^^^^^^^^^

To evaluate membrane performance for a particular method, run below, where method name needs to match where the segmentation files are

.. code-block:: console

   (locpix-env) $ membrane_performance_method -i path/to/project/directory -c path/to/config/file -o method_name

Optionally we can add:

* -m flag to check the metadata of the project before running

To evaluate performance of  membrane segmentation from classic, cellpose and ilastik

.. code-block:: console

   (locpix-env) $ membrane_performance -i path/to/project/directory -c path/to/config/file

Optionally we can add:

* -m flag to check the metadata of the project before running

To aggregate the performance over the folds for methods classic, cellpose without training, cellpose with training and ilastik

.. code-block:: console

   (locpix-env) $ agg_metrics -i path/to/project/directory

**API**
:py:mod:`locpix.scripts.img_seg.membrane_performance_method`
:py:mod:`locpix.scripts.img_seg.membrane_performance`
:py:mod:`locpix.scripts.img_seg.agg_metrics`

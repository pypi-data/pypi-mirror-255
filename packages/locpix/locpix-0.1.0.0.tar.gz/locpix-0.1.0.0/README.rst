locpix
======

**locpix** is a Python library for analysing point cloud data from SMLM.

   This project is under active development

This is a short ReadMe just containing a QuickStart guide.
For more comprehensive documentation please see https://oubino.github.io/locpix/

**locpix** includes the following functionality in order they are used in a normal workflow:

#. `Preprocess`_ : Initialises project and converts .csv files representing SMLM data (point cloud) into .parquet files, **necessary for this software**
#. `Annotate`_ : Generating histograms from the SMLM data and manually annotating these histograms to extract relevant localisations
#. `Get markers`_ : Labelling histogram with seeds for watershed algorithm
#. Segmentation:

   #. `Classic segmentation`_ : Use classic method to segment histograms to extract relevant localisations
   #. `Cellpose segmentation (no training)`_ : Use Cellpose method to segment histograms to extract relevant localisations with no retraining of Cellpose model
   #. `Cellpose segmentation (training)`_ : Use Cellpose method to segment histograms to extract relevant localisations with retraining of Cellpose model
   #. `Ilastik segmentation`_ : Use Ilastik method to segment histograms to extract relevant localisations

#. `Membrane performance`_ : Performance metrics calculation based on the localisations (not the histograms!)

Project Structure
-----------------

We assume your input SMLM data are .csv files.

This input data must first be preprocessed into a user chosen project directory, using the  `Preprocess`_ script.
We strongly suggest this project directory is located outside the locpix folder.

The input and output of all further scripts will remain located inside the project directory, the input data folder
will not be accessed again!

Usage configuration
-------------------

Each script can be run with a GUI, but can also be run in headless mode.

In headless mode each script needs a configuration file (.yaml file), which should be
specified using the -c flag.

Each configuration used, whether run in GUI or headless mode will be saved in the project directory.

The templates for the configuration files can be found in the `templates folder <https://github.com/oubino/locpix/tree/master/src/locpix/templates>`_.

Quickstart
==========

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

To run the script using the GUI, run

.. code-block:: console

   (locpix-env) $ preprocess

To run the script without a GUI -i -c and -o flags should be specified

.. code-block:: console

   (locpix-env) $ preprocess -i path/to/input/data -c path/to/config/file -o path/to/project/directory

Annotate
^^^^^^^^

This script allows for manual segmentation of the localisations.

To run the script using the GUI, run

.. code-block:: console

   (locpix-env) $ annotate

To run the script without a GUI -i and -c flags should be specified

.. code-block:: console

   (locpix-env) $ annotate -i path/to/project/directory -c path/to/config/file

Image segmentation
------------------

Get markers
^^^^^^^^^^^

This script allows for labelling the localisation image with a marker to represent the cells.

To run the script using the GUI, run

.. code-block:: console

   (locpix-env) $ get_markers

To run the script without a GUI -i and -c flags should be specified

.. code-block:: console

   (locpix-env) $ get_markers -i path/to/project/directory -c path/to/config/file

Classic segmentation
^^^^^^^^^^^^^^^^^^^^

Perform classic segmentation on our localisation dataset.

To run the script using the GUI, run

.. code-block:: console

   (locpix-env) $ classic

To run the script without a GUI -i and -c flags should be specified

.. code-block:: console

   (locpix-env) $ classic -i path/to/project/directory -c path/to/config/file

Cellpose segmentation (no training)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   Need to activate extra requirements - these are big and not included in initial install.

   Note that if you have a GPU this will speed this up.

   Note we modified Cellpose to fit in with our analysis, therefore you need to install our forked repository - note below will clone the Cellpose repository to wherever you are located

   If you have a GPU

   .. code-block:: console

      (locpix-env) $ pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu117
      (locpix-env) $ git clone https://github.com/oubino/cellpose
      (locpix-env) $ cd cellpose
      (locpix-env) $ pip install .

   If you don't have a GPU

   .. code-block:: console

      (locpix-env) $ pip install pytorch
      (locpix-env) $ git clone https://github.com/oubino/cellpose
      (locpix-env) $ cd cellpose
      (locpix-env) $ pip install .


Perform Cellpose segmentation on our localisation dataset.

To run the script using the GUI, run

.. code-block:: console

   (locpix-env) $ cellpose_eval

To run the script without a GUI -i and -c flags should be specified

.. code-block:: console

   (locpix-env) $ cellpose_eval -i path/to/project/directory -c path/to/config/file


Cellpose segmentation (training)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   Need to activate extra requirements - these are big and not included in initial install.

   Note that if you have a GPU this will speed this up.

   Note we modified Cellpose to fit in with our analysis, therefore you need to install our forked repository - note below will clone the Cellpose repository to wherever you are located

   If you have a GPU

   .. code-block:: console

      (locpix-env) $ pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu117
      (locpix-env) $ git clone https://github.com/oubino/cellpose
      (locpix-env) $ cd cellpose
      (locpix-env) $ pip install .

   If you don't have a GPU

   .. code-block:: console

      (locpix-env) $ pip install pytorch
      (locpix-env) $ git clone https://github.com/oubino/cellpose
      (locpix-env) $ cd cellpose
      (locpix-env) $ pip install .


Prepare data for training

.. code-block:: console

   (locpix-env) $ cellpose_train_prep -i path/to/project/directory -c path/to/config/file

Train cellpose (using their scripts)

.. code-block:: console

   (locpix-env) $ python -m cellpose --train --dir path/to/project/directory/cellpose_train/train --test_dir path/to/project/directory/cellpose_train/test --pretrained_model LC1 --chan 0 --chan2 0 --learning_rate 0.1 --weight_decay 0.0001 --n_epochs 10 --min_train_masks 1 --verbose

Evaluate cellpose

.. code-block:: console

   (locpix-env) $ cellpose_eval -i path/to/project/directory -c path/to/config/file -u -o cellpose_train_eval


Ilastik segmentation
^^^^^^^^^^^^^^^^^^^^

Need to prepare the data for Ilastik segmentation

.. code-block:: console

   (locpix-env) $ ilastik_prep -i path/to/project/directory -c path/to/config/file

Then run the data through the Ilastik GUI, which needs to be installed from
`Ilastik <https://www.ilastik.org/download.html>`_  and to run it
please see https://oubino.github.io/locpix/user_guide/usage.html#id7

Then convert the output of the Ilastik GUI back into our format

.. code-block:: console

   (locpix-env) $ ilastik_output -i path/to/project/directory -c path/to/config/file

Membrane performance
^^^^^^^^^^^^^^^^^^^^

Need to evaluate the performance of the membrane segmentation

.. code-block:: console

   (locpix-env) $ membrane_performance -i path/to/project/directory -c path/to/config/file

Licenses
--------

+----------------------------------------+----------------------------------------------------------------------+
|                Package                 |                               License                                |
+========================================+======================================================================+
|            alabaster 0.7.12            |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|            app-model 0.1.1             |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|             appdirs 1.4.4              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              arrow 1.2.3               |                              Apache 2.0                              |
+----------------------------------------+----------------------------------------------------------------------+
|            astroid 2.12.13             |                          LGPL-2.1-or-later                           |
+----------------------------------------+----------------------------------------------------------------------+
|            asttokens 2.2.0             |                              Apache 2.0                              |
+----------------------------------------+----------------------------------------------------------------------+
|              attrs 22.1.0              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              Babel 2.11.0              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             backcall 0.2.0             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|  backports.functools-lru-cache 1.6.4   |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|         beautifulsoup4 4.11.1          |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           binaryornot 0.4.4            |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             black 22.12.0              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              build 0.9.0               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              cachey 0.2.1              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|     cellpose 2.1.2.dev26+g731fe4e      |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           certifi 2022.9.24            |                               MPL-2.0                                |
+----------------------------------------+----------------------------------------------------------------------+
|               cfgv 3.3.1               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             chardet 5.1.0              |                                 LGPL                                 |
+----------------------------------------+----------------------------------------------------------------------+
|        charset-normalizer 2.1.1        |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              click 8.1.3               |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|           cloudpickle 2.2.0            |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|             colorama 0.4.6             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|               comm 0.1.3               |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|            commonmark 0.9.1            |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|            contourpy 1.0.6             |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|           cookiecutter 2.1.1           |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             coverage 6.5.0             |                              Apache 2.0                              |
+----------------------------------------+----------------------------------------------------------------------+
|             cycler 0.11.0              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             dask 2022.11.1             |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             debugpy 1.6.4              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            decorator 5.1.1             |                           new BSD License                            |
+----------------------------------------+----------------------------------------------------------------------+
|             distlib 0.3.6              |                            Python license                            |
+----------------------------------------+----------------------------------------------------------------------+
|         docstr-coverage 2.2.0          |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|         docstring-parser 0.15          |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            docutils 0.17.1             |     public domain, Python, 2-Clause BSD, GPL 3 (see COPYING.txt)     |
+----------------------------------------+----------------------------------------------------------------------+
|            entrypoints 0.4             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|          exceptiongroup 1.0.4          |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|            executing 1.2.0             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            fastremap 1.13.3            |                                LGPLv3                                |
+----------------------------------------+----------------------------------------------------------------------+
|             filelock 3.9.0             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              flake8 6.0.0              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            fonttools 4.38.0            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           freetype-py 2.3.0            |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|            fsspec 2022.11.0            |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             HeapDict 1.0.1             |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              hsluv 5.0.3               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            identify 2.5.17             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|                idna 3.4                |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|         imagecodecs 2022.9.26          |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             imageio 2.22.4             |                             BSD-2-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|          imageio-ffmpeg 0.4.7          |                             BSD-2-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|            imagesize 1.4.1             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|        importlib-metadata 6.6.0        |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|             in-n-out 0.1.6             |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|            iniconfig 1.1.1             |                             MIT License                              |
+----------------------------------------+----------------------------------------------------------------------+
|            ipykernel 6.17.1            |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|             ipython 8.13.2             |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|         ipython-genutils 0.2.0         |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              jedi 0.18.2               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              Jinja2 3.1.2              |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|           jinja2-time 0.2.0            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              joblib 1.2.0              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           jsonschema 4.17.3            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|          jupyter-client 7.4.7          |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|           jupyter-core 5.1.0           |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|            kiwisolver 1.4.4            |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|        lazy-object-proxy 1.8.0         |                             BSD-2-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|          line-profiler 4.0.2           |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            llvmlite 0.39.1             |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              locket 1.0.0              |                             BSD-2-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
| locpix 0.0.12.dev70+ga7833b4.d20230120 |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|             magicgui 0.6.1             |                             MIT license                              |
+----------------------------------------+----------------------------------------------------------------------+
|            MarkupSafe 2.1.1            |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|            matplotlib 3.6.2            |                                 PSF                                  |
+----------------------------------------+----------------------------------------------------------------------+
|        matplotlib-inline 0.1.6         |                             BSD 3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|              mccabe 0.7.0              |                            Expat license                             |
+----------------------------------------+----------------------------------------------------------------------+
|         mypy-extensions 0.4.3          |                             MIT License                              |
+----------------------------------------+----------------------------------------------------------------------+
|             napari 0.4.17              |                             BSD 3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|          napari-console 0.0.6          |                             BSD 3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|          napari-locpix 0.0.3           |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|       napari-plugin-engine 0.2.0       |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            napari-svg 0.1.6            |                                BSD-3                                 |
+----------------------------------------+----------------------------------------------------------------------+
|             natsort 8.2.0              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           nest-asyncio 1.5.6           |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             networkx 2.8.8             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|             nodeenv 1.7.0              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|               npe2 0.6.1               |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|              numba 0.56.4              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              numpy 1.23.5              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             numpydoc 1.5.0             |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|    opencv-python-headless 4.6.0.66     |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             packaging 21.3             |                      BSD-2-Clause or Apache-2.0                      |
+----------------------------------------+----------------------------------------------------------------------+
|              pandas 1.5.2              |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|              parso 0.8.3               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              partd 1.3.0               |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            pathspec 0.10.2             |                               MPL 2.0                                |
+----------------------------------------+----------------------------------------------------------------------+
|             pep517 0.13.0              |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|           pickleshare 0.7.5            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              Pillow 9.3.0              |                                 HPND                                 |
+----------------------------------------+----------------------------------------------------------------------+
|              Pint 0.20.1               |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|               pip 23.1.2               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           platformdirs 2.5.4           |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              pluggy 1.0.0              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             polars 0.15.1              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            pre-commit 3.0.3            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           prettytable 3.8.0            |                            BSD (3 clause)                            |
+----------------------------------------+----------------------------------------------------------------------+
|         prompt-toolkit 3.0.33          |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              psutil 5.9.4              |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|             psygnal 0.6.1              |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|            pure-eval 0.2.2             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             pyarrow 10.0.1             |                     Apache License, Version 2.0                      |
+----------------------------------------+----------------------------------------------------------------------+
|           pycodestyle 2.10.0           |                            Expat license                             |
+----------------------------------------+----------------------------------------------------------------------+
|            pydantic 1.10.2             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|       pydata-sphinx-theme 0.12.0       |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|             pyflakes 3.0.1             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            Pygments 2.13.0             |                             BSD License                              |
+----------------------------------------+----------------------------------------------------------------------+
|             PyOpenGL 3.1.6             |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            pyparsing 3.0.9             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              PyQt5 5.15.7              |                                GPL v3                                |
+----------------------------------------+----------------------------------------------------------------------+
|            PyQt5-Qt5 5.15.2            |                               LGPL v3                                |
+----------------------------------------+----------------------------------------------------------------------+
|           PyQt5-sip 12.11.0            |                                 SIP                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           pyrsistent 0.19.2            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              pytest 7.2.0              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            pytest-cov 4.0.0            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|         python-dateutil 2.8.2          |                             Dual License                             |
+----------------------------------------+----------------------------------------------------------------------+
|          python-dotenv 0.21.0          |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|          python-slugify 7.0.0          |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            pytomlpp 1.0.11             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              pytz 2022.6               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            PyWavelets 1.4.1            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              pywin32 304               |                                 PSF                                  |
+----------------------------------------+----------------------------------------------------------------------+
|               PyYAML 6.0               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              pyzmq 24.0.1              |                               LGPL+BSD                               |
+----------------------------------------+----------------------------------------------------------------------+
|            qtconsole 5.4.0             |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|               QtPy 2.3.0               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            requests 2.28.1             |                              Apache 2.0                              |
+----------------------------------------+----------------------------------------------------------------------+
|              rich 12.6.0               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|          scikit-image 0.19.3           |                             Modified BSD                             |
+----------------------------------------+----------------------------------------------------------------------+
|           scikit-learn 1.1.3           |                               new BSD                                |
+----------------------------------------+----------------------------------------------------------------------+
|              scipy 1.9.3               |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|             seaborn 0.12.2             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|           setuptools 67.7.2            |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|          setuptools-scm 7.0.5          |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|               six 1.16.0               |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|         snowballstemmer 2.2.0          |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|         soupsieve 2.3.2.post1          |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              Sphinx 4.5.0              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|          sphinx-autoapi 2.0.0          |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|     sphinxcontrib-applehelp 1.0.2      |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|      sphinxcontrib-devhelp 1.0.2       |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|      sphinxcontrib-htmlhelp 2.0.0      |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|       sphinxcontrib-jsmath 1.0.1       |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|       sphinxcontrib-qthelp 1.0.3       |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|  sphinxcontrib-serializinghtml 1.1.5   |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            stack-data 0.6.2            |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|             superqt 0.4.1              |                         BSD 3-Clause License                         |
+----------------------------------------+----------------------------------------------------------------------+
|           text-unidecode 1.3           |                           Artistic License                           |
+----------------------------------------+----------------------------------------------------------------------+
|          threadpoolctl 3.1.0           |                             BSD-3-Clause                             |
+----------------------------------------+----------------------------------------------------------------------+
|          tifffile 2022.10.10           |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              tomli 2.0.1               |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              toolz 0.12.0              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           torch 1.13.0+cu117           |                                BSD-3                                 |
+----------------------------------------+----------------------------------------------------------------------+
|           torchsummary 1.5.1           |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|        torchvision 0.14.0+cu117        |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              tornado 6.2               |              http://www.apache.org/licenses/LICENSE-2.0              |
+----------------------------------------+----------------------------------------------------------------------+
|              tqdm 4.64.1               |                        MPLv2.0, MIT Licences                         |
+----------------------------------------+----------------------------------------------------------------------+
|            traitlets 5.6.0             |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|              typer 0.7.0               |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|        typing-extensions 4.4.0         |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+
|            Unidecode 1.3.6             |                                 GPL                                  |
+----------------------------------------+----------------------------------------------------------------------+
|            urllib3 1.26.13             |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|           virtualenv 20.17.1           |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              vispy 0.11.0              |                              (new) BSD                               |
+----------------------------------------+----------------------------------------------------------------------+
|             wcwidth 0.2.5              |                                 MIT                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              wheel 0.40.0              |                             MIT License                              |
+----------------------------------------+----------------------------------------------------------------------+
|              wrapt 1.14.1              |                                 BSD                                  |
+----------------------------------------+----------------------------------------------------------------------+
|              zipp 3.15.0               |                               UNKNOWN                                |
+----------------------------------------+----------------------------------------------------------------------+

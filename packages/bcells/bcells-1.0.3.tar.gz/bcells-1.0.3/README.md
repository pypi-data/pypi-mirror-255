# bcells

A Python package to analyze video/image sequence microscopy data regarding the changes in brightness of the visible cells.

# Documentation

## Installation

The package is installable via the Python packet manager `pip`. Thus, a sufficiently new version of Python and the packet manager must be available.

### Installing Python and pip

If Python and pip3 (Python's packet manager) are already installed on your computer you can skip this sectio and go to the section "Installing bcells".

#### Windows

Visit [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) and go to "Stable releases". Then select one of the following installers: Download Windows installer (32-bit), Download Windows installer (64-bit) or Download Windows installer (ARM64) according to your computer (Often, this will the 64-bit version). Follow the instructions of the installer. Python and pip should be installed afterwards. You can check this by opening the command prompt in Windows and type the command `py --version`. Then, the version of Python should be printed. Similarly, `py -m pip --version` should print the version of pip.

#### macOS

Visit [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/) and go to "Stable releases". Then select and download the macOS installer. Follow the instructions of the installer. Python and pip should be installed afterwards. You can check this by opening a terminal and typing the command `python3 --version`. Then, the version of Python should be printed. Similarly, `pip3 --version` should print the version of pip.

#### Linux (Debian or Ubuntu)

Run the following command in a terminal:
```bash
sudo apt install python3 python3-pip
```

Check the installation by typing the following commands in a terminal:
```bash
python3 --version
pip3 --version
```

### Installing bcells

To install bcells, open a command prompt/terminal and type the following command:
Windows: `py -m pip install bcells`
Linux/macOS: `python3 -m pip install bcells`

Furthermore, we recommend installing Jupyter so that the package can be easily be used in a Jupyter notebook. 
Our examples are also written in Jupyter notebooks meaning you can only view those if you have .
This can be done as follows in a command prompt/terminal:
Windows: `py -m pip install notebook`
and Linux/macOS: `python3 -m pip install notebook`

Jupyter notebooks are used as follows:
Open a terminal and type the following command in the command prompt/terminal:
```
jupyter notebook
```
Then, a browser window should open and you can navigate through your computer's file structure. Now, you can either create a new notebook in a desired location or open an existing one.

## Examples

We provide three example files with this package. These are either available in the examples folder of your local installation of the bcells package or can be downloaded from the gitlab repository of the package. 

### Get example files

The simplest way is probably to download these files from the gitlab repository. The example Jupyter notebook files are stored at (https://gitlab.gwdg.de/torben.maass/bcells/-/tree/main/examples)[https://gitlab.gwdg.de/torben.maass/bcells/-/tree/main/examples] and can e.g. be downloaded by clicking the blue "Code" button and then "Download this directory". Now unpack these at your desired location.

Alternatively, open a commmand prompt/terminal and start an interactive Python session by typing `py` on Windows and `python3` on Linux/macOS. Then, type the following commands:
```
>>> import bcells
>>> print(bcells.__file__)
```
This should show the location of the bcells package on your computer. Now, navigate to the examples folder of the package and copy the files to your desired location.

### Run examples

For two of the examples, we need .nd2 image sequence files. These are not provided with the package so you need to make sure that you have some available on your. 

The simplest way to run the examples now, is to first copy the desired example jupyter notebook file (which have ending .ipynb) to the location of the .nd2 file(s). Then, open a terminal a start a Jupyter notebook by typing `jupyter notebook`. Then, a jupyter notebook should start in your browser. Navigate to the location where the .nd2 and .ipynb file(s) are stored. Click on the .ipynb file to open this file. There should be explanations in the notebook on how to run the example. To run the actual code cells either click the "Run" button in the toolbar or press "Shift + Enter" on your keyboard.

## Usage

The (easiest/intended) usage of this package is described in the following.

We assume that the user has multiple .nd2 image sequence files with different drug concentrations. The file names should contain the drug concentration of the experiment corresponding to that file in the following format: ...\_(number)(unit)\_....nd2
In other words, somewhere in the file there should be a section starting and ending with an underscore "_" and in between there should be a number specifying the concentration and the unit which can be either "muM" or "mM" (or µM). There can be whitespace between the number and the unit. For example, a file could be named "ex\_10 muM\_000.nd2" which would get recognised as 10 $\mu$M.

For simple usage, the user can basically copy the `example_usage.ipynb` file from the examples folder of this package inside of the directory where the .nd2 files are stored. Then, the path to this directory is "." (which needs to set in the jupyter notebook). Now, all the code in the jupyter notebook file should be runnable and the package does its job. The resulting data, segmentations and plots should now be viewable in a subfolder which has been created in that directory.

## References

We use code for a unimodalization function from the R package unimonotone.

## License

See [LICENSE.txt](LICENSE.txt)

<!-- ## Citation -->


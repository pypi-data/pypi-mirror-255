# A simple image resizing CLI - PyPi package deployment CI example 

### About
This project is used as an example of how to deploy a Python package to PyPi using GitHub Actions. The example package is a simple CLI tool I built many moons ago that allows you to easily resize any image file from the command line. Feel free to use this if you think it would be useful but you're probably better off with [ImageMagick](https://github.com/ImageMagick/ImageMagick).

### Installation 
```
pip install resize-img
```

### Commands
- `resize-img $IMG_PATH` Saves a new, resized image of the specified image path to the CWD, using the default size of 512x512px.
- `resize-img $IMG_PATH small` Saves specified image as 250x250px in CWD.   
- `resize-img $IMG_PATH medium` Saves specified image as 1000x1000px in CWD.
- `resize-img $IMG_PATH big` Saves specified image as 2000x2000px in CWD.
- `resize-img $IMG_PATH custom <int> <int>` Saves specified image as <int>px<int>px in CWD.
- `resize-img --help` Prints the CLI instructions to your terminal.


## Deploy your own PyPi package with GitHub Actions
**Prerequisites**:

- A [PyPi API token](https://pypi.org/manage/account/token/)
- A [GitHub account](https://github.com/join)

**Setup instructions**

Examples of each of the following steps can be found in this repository in the referenced locations.

1. Add your PyPi username as password to a GitHub repo's environment as secrets.
2. Package the code you want to deploy into a folder _(the package in this example is called img_resizer)_.
3. Create a file named `__init__.py` in your package and import the main function for your package.
4. Create a file named `setup.py` in the root folder of your project. In this file, you specify the name of the PyPi package and any CLI entry points. Package requirements and markdown description can also be specified if you want this to show on the PyPi platform, [see mine for example](https://pypi.org/project/resize-img/). 
5. Create a GitHub Actions workflow to trigger your desired event that will build your package with the `wheel` library and upload your package using the `twine` library. Your PyPi username and password secrets will need to be set as environment variables for this to work _(see my example)_.
6. update your project repo in GitHub to trigger your workflow and upload your package to PyPi. This will then be easily installable on any machine with the command `pip install <package name>`






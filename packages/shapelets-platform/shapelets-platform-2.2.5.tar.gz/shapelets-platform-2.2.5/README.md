![Shapelets](https://shapelets.io/doc/_static/shapeletslogo.png)
-----------------
## Shapelets Platform
[![Downloads](https://static.pepy.tech/badge/shapelets-platform)](https://pepy.tech/project/shapelets-platform)
[![Package Status](https://img.shields.io/pypi/status/shapelets-platform)](https://pypi.org/project/shapelets-platform/)
[![Docker](https://img.shields.io/docker/v/shapeletsdev/shapelets-platform)](https://hub.docker.com/r/shapeletsdev/shapelets-platform)
[![PyPI Latest Release](https://img.shields.io/pypi/v/shapelets-platform)](https://pepy.tech/project/shapelets-platform)

[Docs](https://shapelets.io/doc/contents.html) | [Releases](https://shapelets.io/doc/release_notes/index.html) | [Examples](https://shapelets.io/ebooks-webinars/) | [Resources](https://shapelets.io/resources/)

## Making the most of your data processing platform 

Shapelets is a data science and time series ecosystem for data scientists, and business analysts to bring your ideas to life, and a great opportunity for data engineers and architects to deliver rapid solutions across their organization.

## Why is Shapelets special? 

1. Much faster performance with much less resources. 

2. Accelerated development of time series analytics. 

3. Unlimited users and pay per use. 

## Getting Started 

Develop accelerated solutions that integrate seamlessly with your data ecosystem. 

### Install 

To install a binary distribution, the only requirement is to have a working (recent, 3.7.3 and onwards) version of Python in your system. If you don’t have Python yet you can download it here. 

### PIP 
To install Shapelets using pip, you can install with:

```sh
pip install shapelets-platform
```

<b>Note:</b>
    
    It’s a good idea to use a virtual environment or a docker to avoid conflicts between libraries installed on your system. If you are not familiar with these methods, you can find instructions below. 


If you want want to use the Virtual File System (VFS) feature, you need to install the drivers. You can do it with:

```sh
pip install shapelets-platform[vfs-all]
```

**Alert**: With the `all` option, you will install all the drivers. We currently support **Azure Blob Storage Gen1 & Gen2**, **Server Message Block (SMB)** and the local filesystem. Other fsspec-compatible protocols will be available soon.       
   

To check if Shapelets is installed, you can execute:

```sh
python -c "import shapelets as sh; print(sh.__version__)"
```

It's a good idea to use a virtual environment or docker image, to avoid conflicts between versions.

**Conda**
Currently, conda installation is not available. 

### Virtual environment

If you want to install shapelets on a safe environment, you could also create a virtual environment that will help you to safely install shapelets without risking any corruptions.  I will show you in the following lines how to do this.  

First you want to create a directory  
`mkdir shapelets_ws`
Then you will change directory 
`cd shapelets_ws`
And you will create the virtual environment in the directory  
`virtualenv venv`
Afterward you will activate the virtual environment 
`source ./venv/bin/activate`
Finaly you can use the pip install command to install shapelets in this environment.  


### Docker 

If you want to install Shapelets on a Docker container, we recommend you use our Docker Image, you can download it with:

`docker pull shapeletsdev/shapelets-platform:latest`

If you wish to install Shapelets on a Docker container, we recommend using our Docker image. You can download it with:

`docker run --name shapelets -p 4567:4567 -d -v /[...]:/io shapeletsdev/shapelets-platform:latest`

[...] = insert your own directory  

This Docker image needs to expose the *4567* port, and we recommend that you create a volume to share your local scripts with the Docker container.  

Now open your web browser and try `http://localhost:4567`


### Recommendations

Once you install Shapelets, you are ready to use it. If you want a recommendation about development environments, we recommend you:

- To write and execute code interactively for exploratory data analysis and processing, use notebooks in [JupyterLab](https://jupyter.org/install).
- To write large scripts for processing data or build DataApps use an IDE, like  [Visual Studio Code](https://code.visualstudio.com/).  


## Helpful links 

- [Documentation](https://shapelets.io/doc/contents.html)
- [Releases](https://shapelets.io/doc/release_notes/index.html)
- [Examples](https://shapelets.io/ebooks-webinars/)

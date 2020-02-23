# odsclient

*A nonofficial client for OpenDataSoft API.*

[![Python versions](https://img.shields.io/pypi/pyversions/odsclient.svg)](https://pypi.python.org/pypi/odsclient/) [![Build Status](https://travis-ci.org/smarie/python-odsclient.svg?branch=master)](https://travis-ci.org/smarie/python-odsclient) [![Tests Status](https://smarie.github.io/python-odsclient/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-odsclient/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-odsclient/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-odsclient)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-odsclient/) [![PyPI](https://img.shields.io/pypi/v/odsclient.svg)](https://pypi.python.org/pypi/odsclient/) [![Downloads](https://pepy.tech/badge/odsclient)](https://pepy.tech/project/odsclient) [![Downloads per week](https://pepy.tech/badge/odsclient/week)](https://pepy.tech/project/odsclient) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-odsclient.svg)](https://github.com/smarie/python-odsclient/stargazers)

`odsclient` provides a minimal set of functions to grab a dataset or a collection of datasets from an OpenDataSoft platform. 

It initial purpose is not to cover the full Search API available - although contributions towards that direction are welcome.

## Installing

```bash
> pip install odsclient
```

If you wish to download datasets as dataframes, you should also install `pandas`. This is not mandatory, though.

## Usage

### 1. Basics

#### a- Downloading a "flat" dataset

The most basic thing that you can do is to download a whole dataset, similarly to what you can get when clicking on the links with your browser on a dataset's ["Export" page](https://public.opendatasoft.com/explore/dataset//world-growth-since-the-industrial-revolution0/download/):

```python
from odsclient import get_whole_dataset

csv_str = get_whole_dataset("world-growth-since-the-industrial-revolution0", 
                            platform_id='public')
print(csv_str)
```

yields

```
Year Ending;World output;World population;Per capita output
2012-12-31;3.03783837;1.39292748;1.62231324
1700-12-31;0.07352168;0.05783974;0.01567288
1820-12-31;0.51654477;0.44594248;0.07028884
1913-12-31;1.48929571;0.58556427;0.89847031
```

If you have `pandas` installed, you can get the dataset directly as a dataframe:

```python
from odsclient import get_whole_dataframe

df = get_whole_dataframe("world-growth-since-the-industrial-revolution0", 
                         platform_id='public')
print(df)
```

yields

```
  Year Ending  World output  World population  Per capita output
0  1820-12-31      0.516545          0.445942           0.070289
1  1913-12-31      1.489296          0.585564           0.898470
2  2012-12-31      3.037838          1.392927           1.622313
3  1700-12-31      0.073522          0.057840           0.015673
```

### 2. Advanced

**TODO**

## Main features / benefits

 - Simple access to ODS API to retrive a whole dataset

## See Also

This library was inspired by:

 * [`azmlclient`](https://smarie.github.io/python-azureml-client/)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-odsclient](https://github.com/smarie/python-odsclient)

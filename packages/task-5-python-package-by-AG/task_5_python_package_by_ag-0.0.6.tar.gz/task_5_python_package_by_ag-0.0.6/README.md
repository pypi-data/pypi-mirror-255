# Task 5 Python Package by Anton Galkin



## Description

The package contains a program that counts the number of authentic characters in a string.<br/>
To download data, you can specify the following parameters
when starting the program in the terminal: <br/>
  --string "your string"  
  --file path_your_file

## Project structure

task_5_python_package  
│  
├── application  
│ ├── `__init.py__`  
│ └── app.py  
│  
└── `__main__.py`  

## Installation

To install the package, input the following in your terminal:
```bash
python3 pip install task_5_python_package_by_AG
```


## Usage

### Run package in CLI with String Argument:
```
task_5_python_package_by_AG --string "your string"
```
Example:
```
task_5_python_package_by_AG --string "aabcdeeff"
```


### Run package in CLI with File Argument:
```
task_5_python_package_by_AG --file path_your_file
```
Example:
```
task_5_python_package_by_AG --file /home/anton/Documents/test_text
```

### Import in python console
Example:

```
from task_5_python_package_by_AG import count_authentic_signs
```

```
python -c 'from task_5_python_package_by_AG import cli(); cli()' --string "aabcdeefff"
```

```
python -c 'from task_5_python_package_by_AG import cli(); cli()' --file home/anton/Documents/test-text
```


***

## Authors and acknowledgment
Anton Galkin

## License
MIT

## Project status
Study

LC Margin
==============================

The simple tool for calculate LC margin

### Quick setup

> The next steps assume that conda is already installed

1 - <a name="step-1">Create a conda environment:</a>


```bash
conda create python=3.8 -n lc_margin
```
2 - <a name="step-2">Activate the conda environment</a>

```bash
conda activate lc_margin
```

3 - <a name="step-3">Install the project basic dependencies and development dependencies</a>

> Make sure you are inside the root project directory before executing the next commands.
>
> The root project directory is the directory that contains the `manage.py` file

On Linux and Mac

```bash
pip install -r requirements/local.txt
```

On Windows

```bash
pip install -r requirements\local.txt
```
4 - <a name="step-4">Modify allow IP at config/settings/local.py</a>

```python
...
# add your IP at list
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
...
```


```bash
python manage.py migrate
```


### <a name="running-tests">Running the tests and coverage test</a>


```bash
coverage run -m pytest
```

## Modify

### Models

1. The models are save at `lc_margin/main/tools/models`
2. The model loader and one-hot encoding setting is at the `__init__` at `LCMarginCalculator` in `lc_margin/main/tools/utils.py`.

### Options

1. All the options are save in `lc_margin/main/models.py`
2. Just follow the format to add or modify the option, and don't forget to change the one-hot encoding either.
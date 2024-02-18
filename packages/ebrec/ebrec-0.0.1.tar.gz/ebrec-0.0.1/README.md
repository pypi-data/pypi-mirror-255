
# Requirements
```
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
python3 -m pip install --upgrade setuptools wheel
```

# Download repository: 
``` 
git clone https://github.com/johanneskruse/pypi_template.git
```

# Upload:

In *pyproject.toml* you can set the name of the pacakage

## Run the following to upload: 
[Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
### Generating distribution archives
Stand inside the project, i.e.
```
cd pypi_template
```
Next build the package:
```
python3 -m build
```

This command should output a lot of text and once completed should generate two files in the dist directory:
```
dist/
├── sampleproject-0.0.1-py3-none-any.whl
└── sampleproject-0.0.1.tar.gz
```
### Uploading the distribution archives
```
twine upload dist/*
```

Go to https://pypi.org/ to see the package! 


# Inspiration
[setup.py vs setup.cfg in Python](https://towardsdatascience.com/setuptools-python-571e7d5500f2#:~:text=be%20more%20appropriate.-,The%20setup.,as%20the%20command%20line%20interface.)

[sample git repo project](https://github.com/pypa/sampleproject)

[Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

TODO: 
- Setup with pyproject.toml file
- Note that if you want to install packages in editable mode (i.e. by running pip install -e .) you must have a valid setup.py file apart from setup.cfg and pyproject.toml. TRY TO RUN INSTEAD: pip install -e . -f .

# Acronym Generator (help generate the name)

https://acronymify.com/

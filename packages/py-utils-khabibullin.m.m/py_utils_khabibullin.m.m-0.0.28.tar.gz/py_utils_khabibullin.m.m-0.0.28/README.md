# Example
https://github.com/pypa/sampleproject
https://packaging.python.org/en/latest/tutorials/packaging-projects/

# Example Package

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

# PREREQUESITES
To be able to build, install "python -m pip install --upgrade build"
To be able to upload build, install twin "python -m pip install --upgrade twine"

# DEPLOY
Update version
Remove "dist" folder
python -m build
## To PyPl
python -m twine upload dist/*
## To TestPyPl
python -m twine upload --repository testpypi dist/*

# INSTALL
## From PyPl
pip install py-utils-khabibullin.m.m
## From TestPyPl
pip install py-utils-khabibullin.m.m --index-url https://test.pypi.org/simple/

# UPGRADE
pip install -U py-utils-khabibullin.m.m
pip install -U py-utils-khabibullin.m.m --index-url https://test.pypi.org/simple/

# UNINSTALL
pip uninstall py-utils-khabibullin.m.m

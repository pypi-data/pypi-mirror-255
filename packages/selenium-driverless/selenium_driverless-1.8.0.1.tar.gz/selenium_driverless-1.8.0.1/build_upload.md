## Build dist
```shell
python setup.py sdist -v
```

## Upload to pypi
```shell
twine upload --repository selenium-driverless dist/*
```

## run docs
```shell
D:\System\Lib\Python\Python310\python.exe -m sphinx.cmd.build docs/docs_source docs dirhtml
```

## install all python versions from dir
```shell
# 3.7
pip install C:\Users\aurin\PycharmProjects\selenium_driverless
```

## install all python versions from pypi
```shell
# 3.7
pip uninstall -y selenium_driverless;
pip install --no-cache-dir --upgrade selenium_driverless
```

## install from GitHub
```shell
pip install https://github.com/kaliiiiiiiiii/Selenium-Driverless/archive/refs/heads/master.zip
```
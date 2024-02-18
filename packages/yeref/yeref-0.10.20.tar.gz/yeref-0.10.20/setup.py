from setuptools import setup

setup(
    name='yeref',
    version='0.10.20',
    description='desc-f',
    author='john smith',
    packages=['yeref'],
    # install_requires=[
    #       "httplib2>=0.20.4",
    #       "moviepy>=1.0.3",
    #       "Pillow>=9.2.0",
    #       "aiogram>=2.22.1",
    #       "loguru>=0.6.0",
    #       "oauth2client>=4.1.3",
    #       "google-api-python-client>=2.61.0",
    #       "telegraph>=2.1.0",
    #       "setuptools>=65.3.0",
    # ]
)

# endregion

# python -m build; twine upload --repository yeref dist/*; python3 -m pip install --upgrade yeref ; python3 -m pip install --upgrade yeref
# python3 -m pip install --upgrade yeref

# python3 -m pip install --force-reinstall /Users/mark/PycharmProjects/AUTOBOT/yeref/dist/yeref-0.5.58-py3-none-any.whl
# pip install --force-reinstall -v "yeref==0.1.30"
# pip install --force-reinstall -v "pydantic[dotenv]==1.10.12"
# pip install aiogram==3.0.0b8
# pip install -U g4f==0.1.9.0

# pip install https://github.com/aiogram/aiogram/archive/refs/heads/dev-3.x.zip
# pip show aiogram
# ARCHFLAGS="-arch x86_64" pip install pycurl

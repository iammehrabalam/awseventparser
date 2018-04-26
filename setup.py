from setuptools import setup, find_packages

setup(
    name='awseventparser',
    version='0.1',
    packages=find_packages(),
    author='Md Mehrab Alam',
    author_email='md.mehrab@gmail.com',
    url='github.com/iammehrabalam/awseventparser',
    description='Small wrapper to aws event and return data',
    install_requires=['boto3'],
    test_suite='test',
)
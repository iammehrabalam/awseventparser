from setuptools import setup, find_packages

setup(
    name='awseventparser',
    version='0.4',
    packages=find_packages(),
    author='Md Mehrab Alam',
    author_email='md.mehrab@gmail.com',
    long_description=open('README.md').read(),
    url='https://github.com/iammehrabalam/awseventparser',
    description='Small wrapper to aws event and return data',
    install_requires=['boto3'],
    test_suite='test',
)
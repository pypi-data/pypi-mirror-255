from setuptools import setup, find_packages

setup(
    name='texsupport',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'texsupport = texsupport.converter:main',
        ],
    },
    install_requires=[
        'texsupport'
    ],
    author='Taylor Turner',
    author_email='resume.tturner@gmail.com',
    description='A package to convert and support TeX files.',
    url='https://github.com/ifTaylor/texsupport'
)

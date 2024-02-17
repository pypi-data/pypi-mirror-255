from setuptools import setup, find_packages

setup(
    name='dj_matool',
    version='0.1.1',
    author='Darshit Joshi',
    author_email='darshitj@dosepack.com',
    description='this is a migration automation tool to ease the process of migration for multiple environments',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

from setuptools import setup, find_packages

setup(
    name='amicus_interfaces',
    version='0.1.1',
    author='Christian Mauceri',
    author_email='christian@example.com',
    description='Un package pour les interfaces communes d\'amicus.',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
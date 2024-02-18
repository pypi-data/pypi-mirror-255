from setuptools import setup, find_packages

setup(
    name='SunFlowerRainbow',
    version='0.1.0',
    author='Big JE',
    author_email='jeanchristophegaudreau@hotmail.com',
    description='A short description of your project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CoffeeBeans007/tradeapp.git',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'pandas',
        'colored', # Add any other dependencies your package needs
    ],
)
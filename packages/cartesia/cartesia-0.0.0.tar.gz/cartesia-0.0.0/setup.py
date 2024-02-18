from setuptools import setup, find_packages

setup(
    name='cartesia',
    version='0.0.0',
    author='Kabir Goel',
    author_email='kabir@cartesia.ai',
    description='Library for the Cartesia API.',
    packages=find_packages(),
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


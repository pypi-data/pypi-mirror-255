from setuptools import setup, find_packages

setup(
    name='vilpi',  
    version='0.1',  
    packages=find_packages(),  
    description='Python package for visualizing PyTorch models',
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',
    author='Vladyslav',
    author_email='vladdikiy17@gmail.com',  
    url='https://github.com/dykyivladk1/vilpi',  
    install_requires=[
        'matplotlib',  
        'torch',
    ],
    classifiers=[
        
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

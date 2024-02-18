from setuptools import setup, find_packages
from datetime import datetime


version = datetime.now().strftime('%Y%m%d%H%M')

setup(
    name='tui_dsmt',
    version=version,
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='everything you need for our jupyter notebooks',
    long_description='everything you need for our jupyter notebooks',
    long_description_content_type='text/markdown',
    url='https://dbgit.prakinf.tu-ilmenau.de/lectures/data-science-methoden-und-techniken',
    project_urls={},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.10',
    install_requires=[
        'jupyter',
        'ipywidgets',
        'checkmarkandcross',
        'networkx~=3.2.1',
        'plotly~=5.18.0',
        'pandas~=2.2.0',
        'pyarrow~=15.0.0',
        'scikit-learn~=1.4.0'
    ],
    package_data={},
    include_package_data=True
)

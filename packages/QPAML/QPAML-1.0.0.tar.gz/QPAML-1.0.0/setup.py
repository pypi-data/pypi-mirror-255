from setuptools import setup, find_packages
from sys import version_info
import os
import io
from warnings import warn, filterwarnings


if version_info[:2] != (3, 8):
    filterwarnings("always", category=DeprecationWarning)
    warn(
        "QPAML was tested with Python 3.8. Issues may occur with other versions.",
        category=DeprecationWarning,
    )

setup(
    name = 'QPAML',
    version ='1.0.0',
    author = 'Miguel Angel Ramos-Valdovinos',
    author_email = 'miguel.ramos@cinvestav.mx',
    description = 'A package to classify metabolic reactions that affect production of metabolites.',
    license = "Apache 2.0",
    classifiers=['Development Status :: 4 - Beta'],
    packages=['QPAML'],
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'QPAML': ['*']},
    install_requires=[
        'cameo==0.13.6',
        'cobra==0.22.0',
        'MarkupSafe==2.0.1',
        'networkx==3.1',
        'psutil==5.9.5',
        'seaborn==0.12.2',
        'lime==0.2.0.1',
        'scikit-learn==1.3.0',
        'numpy==1.23.5',
        'tqdm==4.66.1'
    ],
    url='https://gitlab.com/amalib/qpaml',
    python_requires='==3.8.0',
    keywords=['metabolic engineering', 'Flux Balance Analysis', 'Qualitative Perturbation Analysis', 'Qualitative Lineal Model', 'Metabolic model'],
    platforms=['Platform-Independent'],     
    #scripts=['uninstall.py'],
    #py_modules=['QPAML'],
)

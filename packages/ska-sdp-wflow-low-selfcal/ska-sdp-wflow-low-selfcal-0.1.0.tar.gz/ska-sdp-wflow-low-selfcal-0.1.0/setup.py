# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ska_sdp_wflow_low_selfcal',
 'ska_sdp_wflow_low_selfcal.pipeline',
 'ska_sdp_wflow_low_selfcal.pipeline.support']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.2.2,<6.0.0',
 'bdsf>=1.10.2,<2.0.0',
 'everybeam>=0.5.1,<0.6.0',
 'h5py>=3.8.0,<4.0.0',
 'losoto>=2.4.1,<3.0.0',
 'lsmtool==1.4.11',
 'pathlib>=1.0.1,<2.0.0',
 'pluggy>=1.0.0,<2.0.0',
 'python-casacore>=3.5.2,<4.0.0',
 'requests>=2.28.2,<3.0.0',
 'shapely>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'ska-sdp-wflow-low-selfcal',
    'version': '0.1.0',
    'description': 'SKA LOW selfcal pipeline',
    'long_description': None,
    'author': 'chiarasal',
    'author_email': 'chiara.salvoni@cgi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)

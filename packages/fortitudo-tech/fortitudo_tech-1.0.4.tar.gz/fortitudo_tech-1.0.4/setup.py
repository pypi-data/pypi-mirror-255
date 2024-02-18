# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tech']

package_data = \
{'': ['*'], 'tech': ['data/*']}

install_requires = \
['cvxopt>=1.3.0,<2.0.0',
 'matplotlib>=3.4,<4.0',
 'numpy>=1.22,<2.0',
 'pandas>=1.3.4',
 'scipy>=1.10,<2.0']

setup_kwargs = {
    'name': 'fortitudo-tech',
    'version': '1.0.4',
    'description': 'Conditional Value-at-Risk (CVaR) portfolio optimization and Entropy Pooling views / stress-testing in Python.',
    'long_description': ".. image:: https://github.com/fortitudo-tech/fortitudo.tech/actions/workflows/tests.yml/badge.svg\n   :target: https://github.com/fortitudo-tech/fortitudo.tech/actions/workflows/tests.yml\n\n.. image:: https://codecov.io/gh/fortitudo-tech/fortitudo.tech/graph/badge.svg?token=Z16XK92Gkl \n   :target: https://codecov.io/gh/fortitudo-tech/fortitudo.tech\n\n.. image:: https://mybinder.org/badge_logo.svg\n   :target: https://mybinder.org/v2/gh/fortitudo-tech/fortitudo.tech/main?labpath=examples\n\nFortitudo Technologies Open Source\n==================================\n\nThis package allows you to explore open-source implementations of some of our\nfundamental technologies, e.g., Entropy Pooling and CVaR optimization in Python.\nSee this `YouTube playlist <https://www.youtube.com/playlist?list=PLfI2BKNVj_b2rurUsCtc2F8lqtPWqcs2K>`_\nfor a walkthrough of the package's functionality and examples. For a high-level\nintroduction to the investment framework, see this `YouTube video <https://youtu.be/4ESigySdGf8>`_\nand `Medium article <https://medium.com/@ft_anvo/entropy-pooling-and-cvar-portfolio-optimization-in-python-ffed736a8347>`_.\nFor an in-depth mathematical introduction to the investment framework, see\nthese `SSRN articles <https://ssrn.com/author=2738420>`_.\n\nThe package is intended for advanced users who are comfortable specifying\nportfolio constraints and Entropy Pooling views using matrices and vectors.\nThis gives full flexibility in relation to working with these technologies.\nHence, input checking is intentionally kept to a minimum.\n\nIf you like this package, we invite you to show your support by giving it a\nGitHub star. The greater the number of stars it receives, the more time and\nenergy we will invest in enhancing its functionality and providing additional\nexamples.\n\nFortitudo Technologies offers novel investment software as well as quantitative\nand digitalization consultancy to the investment management industry. For more\ninformation, please visit our `website <https://fortitudo.tech>`_.\n\nInstallation Instructions\n-------------------------\n\nInstallation can be done via pip::\n\n   pip install fortitudo.tech\n\nFor best performance, we recommend that you install the package in a `conda environment\n<https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_\nand let conda handle the installation of dependencies before installing the\npackage using pip. You can do this by following these steps::\n\n   conda create -n fortitudo.tech -c conda-forge python scipy pandas matplotlib cvxopt\n   conda activate fortitudo.tech\n   pip install fortitudo.tech\n\nThe examples might require you to install additional packages, e.g., seaborn and\nipykernel / notebook / jupyterlab if you want to run the notebooks. Using pip to\ninstall these packages should not cause any dependency issues.\n\nYou can also explore the examples in the cloud without any local installations using\n`Binder <https://mybinder.org/v2/gh/fortitudo-tech/fortitudo.tech/main?labpath=examples>`_.\nHowever, note that Binder servers have very limited resources and might not support\nsome of the optimized routines this package uses. If you want access to a stable\nand optimized environment with persistent storage, please subscribe to our Data\nScience Server.\n\nDisclaimer\n----------\n\nThis package is completely separate from our proprietary solutions and therefore\nnot representative of the quality and functionality offered by the Investment Simulation\nand Investment Analysis modules. If you are an institutional investor who wants to\nexperience how these methods can be used for sophisticated analysis in practice,\nplease request a demo by sending an email to demo@fortitudo.tech.\n",
    'author': 'Fortitudo Technologies',
    'author_email': 'software@fortitudo.tech',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://fortitudo.tech',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.13',
}


setup(**setup_kwargs)

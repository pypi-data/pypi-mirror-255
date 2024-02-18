# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pplog',
 'pplog.azure',
 'pplog.config',
 'pplog.dbricks',
 'pplog.dbu_estimation',
 'pplog.errors',
 'pplog.factory',
 'pplog.formatters',
 'pplog.handlers',
 'pplog.hooks',
 'pplog.integrations',
 'pplog.integrations.great_expectations',
 'pplog.integrations.http',
 'pplog.log_checks',
 'pplog.logging',
 'pplog.time_tracking',
 'pplog.unhandled_exception']

package_data = \
{'': ['*'], 'pplog': ['ppconf/*']}

install_requires = \
['azure-eventgrid>=4.16.0,<5.0.0',
 'azure-identity>=1.15.0,<2.0.0',
 'databricks-sdk>=0.18.0,<0.19.0',
 'great-expectations>=0.18.8,<0.19.0',
 'logstash-formatter>=0.5.17,<0.6.0',
 'omegaconf>=2.3.0,<3.0.0',
 'pyspark>=3.3.2']

setup_kwargs = {
    'name': 'pplog',
    'version': '0.1.19',
    'description': 'Pricing Domain Logging and Monitoring Tool',
    'long_description': '# Introduction \nTODO: Give a short introduction of your project. Let this section explain the objectives or the motivation behind this project. \n\n# Getting Started\nTODO: Guide users through getting your code up and running on their own system. In this section you can talk about:\n1.\tInstallation process\n2.\tSoftware dependencies\n3.\tLatest releases\n4.\tAPI references\n\n# Build and Test\nTODO: Describe and show how to build your code and run the tests. \n\n# Contribute\nTODO: Explain how other users and developers can contribute to make your code better. \n\nIf you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:\n- [ASP.NET Core](https://github.com/aspnet/Home)\n- [Visual Studio Code](https://github.com/Microsoft/vscode)\n- [Chakra Core](https://github.com/Microsoft/ChakraCore)',
    'author': 'Paolo Andreas Stall Rechia',
    'author_email': 'paolo_andreas.stall_rechia@mail.schwarz',
    'maintainer': 'Paolo Andreas Stall Rechia',
    'maintainer_email': 'paolo_andreas.stall_rechia@mail.schwarz',
    'url': 'https://dev.azure.com/schwarzit/schwarzit.ai-public/_git/pplog',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

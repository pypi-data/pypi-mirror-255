# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prefect_dbt_flow', 'prefect_dbt_flow.dbt', 'prefect_dbt_flow.utils']

package_data = \
{'': ['*']}

install_requires = \
['prefect>=2.7,<3.0']

setup_kwargs = {
    'name': 'prefect-dbt-flow',
    'version': '0.5.6',
    'description': 'Prefect - dbt integration',
    'long_description': '<p align="center">\n  <a href="https://dataroots.io"><img alt="Maintained by dataroots" src="https://dataroots.io/maintained-rnd.svg" /></a>\n  <a href="https://pypi.org/project/prefect-dbt-flow/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/prefect-dbt-flow" /></a>\n  <a href="https://pypi.org/project/prefect-dbt-flow/"><img alt="PiPy" src="https://img.shields.io/pypi/v/prefect-dbt-flow" /></a>\n  <a href="https://pepy.tech/project/prefect-dbt-flow"><img alt="Downloads" src="https://pepy.tech/badge/prefect-dbt-flow" /></a>\n  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>\n  <a href="http://mypy-lang.org/"><img alt="Mypy checked" src="https://img.shields.io/badge/mypy-checked-1f5082.svg" /></a>\n  <a href="https://codecov.io/gh/datarootsio/prefect-dbt-flow" >\n    <img src="https://codecov.io/gh/datarootsio/prefect-dbt-flow/graph/badge.svg?token=NQ6RMX6670"/>\n  </a>\n</p>\n\n# prefect-dbt-flow\nprefect-dbt-flow is a Python library that enables Prefect to convert dbt workflows into independent tasks within a Prefect flow. This integration simplifies the orchestration and execution of dbt models and tests using Prefect, allowing you to build robust data pipelines and monitor your dbt projects efficiently.\n\ndbt is an immensely popular tool for building and testing data transformation models, and Prefect is a versatile workflow management system. This integration brings together the best of both worlds, empowering data engineers and analysts to create robust data pipelines.\n\nKey features:\n\n - *Simplified Orchestration*: Define and manage your dbt projects and models as Prefect tasks, creating a seamless pipeline for data transformation.\n - *Monitoring and Error Handling*: Gain deep insights into the execution of your dbt workflows and take immediate action in case of issues.\n - *Workflow Consistency*: Ensure your dbt workflows run consistently by managing them through Prefect. This consistency is crucial for maintaining data quality and reliability.\n - *Advanced Configuration*: Customize your dbt workflow by adjusting the dbt project, profile, and DAG options. You can also use Prefect features like scheduling, notifications, and task retries to monitor and manage your dbt flows effectively.\n\nTo get started, check out our [getting started guide](https://datarootsio.github.io/prefect-dbt-flow/latest/getting_started/).\n\n**Active Development Notice:** *prefect-dbt-flow is actively under development and may not be ready for production use. We advise users to be aware of potential breaking changes as the library evolves. Please check the changelog for updates.*\n\n## How to Install\nYou can install prefect-dbt-flow via pip:\n```shell\npip install prefect-dbt-flow\n```\n\n*Note*: prefect-dbt-flow does not come with dbt as a dependency. You will need to install dbt or a dbt-adapter separately.\n\n## Basic Usage\nHere\'s an example of how to use prefect-dbt-flow to create a Prefect flow for your dbt project:\n\n```python\nfrom prefect_dbt_flow import dbt_flow\nfrom prefect_dbt_flow.dbt import DbtProfile, DbtProject\n\nmy_flow = dbt_flow(\n    project=DbtProject(\n        name="jaffle_shop",\n        project_dir="path_to/jaffle_shop",\n        profiles_dir="path_to/jaffle_shop",\n    ),\n    profile=DbtProfile(\n        target="dev",\n        overrides={\n            "type": "duckdb",\n            "path": "path_to/duckdb.db",\n        },\n    ),\n)\n\nif __name__ == "__main__":\n    my_flow()\n```\n\n<img src="https://raw.githubusercontent.com/datarootsio/prefect-dbt-flow/main/docs/images/jaffle_shop_dag.png" alt="jaffle_shop_dag" width="100%">\n\nFor more information consult the [docs](https://datarootsio.github.io/prefect-dbt-flow/)\n\n## Inspiration\nprefect-dbt-flow draws inspiration from various projects in the data engineering and workflow orchestration space, including:\n- [astronomer-cosmos](https://github.com/astronomer/astronomer-cosmos)\n- [dbt + Dagster](https://docs.dagster.io/integrations/dbt)\n- [prefect-dataplatform - Anna Geller](https://github.com/anna-geller/prefect-dataplatform)\n\n# License\nThis project is licensed under the MIT License. You are free to use, modify, and distribute this software as per the terms of the license. If you find this project helpful, please consider giving it a star on GitHub.\n',
    'author': 'David Valdez',
    'author_email': 'david@dataroots.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://datarootsio.github.io/prefect-dbt-flow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

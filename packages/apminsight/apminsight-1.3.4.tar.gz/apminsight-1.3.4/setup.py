
from setuptools import setup, find_packages
from apminsight import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='apminsight',
      version=version,
      description='Site24x7 application performance monitoring',
      url='https://site24x7.com',
      author='Zoho Corporation Pvt. Ltd.',
      author_email='apm-insight@zohocorp.com',
      maintainer='ManageEngine Site24x7',
      maintainer_email='apm-insight@zohocorp.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='LICENSE.txt',
      packages=find_packages(exclude=['tests', 'tests.*']),
      include_package_data = True,
      python_requires='>=3.6',
      install_requires=[
            "requests",
            "psutil"
      ],
      entry_points={
            "console_scripts":[
                  "apminsight-run = apminsight.apm_run:main",
            ],
      },
      zip_safe=False)

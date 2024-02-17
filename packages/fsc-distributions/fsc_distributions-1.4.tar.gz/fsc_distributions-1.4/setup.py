from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "fsc_distributions/README.md").read_text()

setup(name='fsc_distributions',
      version='1.4',
      author='FarahS',
      long_description=long_description,
      long_description_content_type='text/markdown',
      description='Gaussian and binomial distribution classes',
      packages=['fsc_distributions'],
      zip_safe=False)

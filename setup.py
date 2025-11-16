from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mn_hotel_rates/__init__.py
from mn_hotel_rates import __version__ as version

setup(
	name="mn_hotel_rates",
	version=version,
	description="Hotel contract and rate management system",
	author="Your Company",
	author_email="info@yourcompany.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

from setuptools import find_packages
from setuptools import setup

from wagtailcache import __version__


with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

setup(
    name="cjkcms-cache",
    version=__version__,
    author="Grzegorz Krol",
    author_email="info@cjkcms.com",
    url="https://github.com/cjkpl/cjkcms-cache",
    description="A simple page cache for Wagtail based on the Django cache middleware. Forked from wagtail-cache.",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="BSD license",
    include_package_data=True,
    packages=find_packages(),
    install_requires=["wagtail>=3.0,<7"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 3",
        "Framework :: Wagtail :: 4",
        "Framework :: Wagtail :: 5",
    ],
)

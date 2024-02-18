import codecs
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.3'
DESCRIPTION = 'Simple django rest media manager'
LONG_DESCRIPTION = ('This library is created based on CQRS and domain driven design in order to understand the underlying structure of this '
                    'architecture')
with open(file='django_simple_media_manager/requirements.txt') as file:
    REQUIREMENTS = [requirement.rsplit() for requirement in file]

# Setting up
setup(
    name="django-simple-media-manager",
    version=VERSION,
    author="Ali Seylaneh",
    author_email="aliseylaneh@gmail.com",
    url="https://hamgit.ir/aliseylaneh/media-manager",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    keywords=['python', 'video', 'media', 'django', 'domain-driven-design', 'CQRS'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: Django",

    ],
    include_package_data=True,

)

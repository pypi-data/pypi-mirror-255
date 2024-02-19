from setuptools import find_packages, setup

import versioneer

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()
with open("requirements.txt", "r") as f:
    REQUIREMENTS = [line.strip() for line in f]

CLASSIFIERS = [
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 4.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.11",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
]

setup(
    author_email="shawn.coding.acc@gmail.com",
    author="Shawn Ng",
    classifiers=CLASSIFIERS,
    cmdclass=versioneer.get_cmdclass(),
    description="A Django application that provides generic utility.",
    install_requires=REQUIREMENTS,
    license="BSD-3",
    long_description=LONG_DESCRIPTION,
    name="django-util",
    packages=find_packages(include=["django_util", "django_util.*"]),
    platforms="any",
    test_suite="nose.collector",
    tests_require=["nose"],
    url="https://github.com/shawnngtq/django-util",
    version=versioneer.get_version(),
)

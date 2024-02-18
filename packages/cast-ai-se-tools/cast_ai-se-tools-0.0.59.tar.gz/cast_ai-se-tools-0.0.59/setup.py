from setuptools import setup, find_packages
import os

with open(os.path.join('version.txt')) as version_file:
    version_from_file = version_file.read().strip()

with open('requirements.txt') as f_required:
    required = f_required.read().splitlines()

with open('test_requirements.txt') as f_tests:
    required_for_tests = f_tests.read().splitlines()

setup(
    name="cast_ai-se-tools",
    author="Dan Amzulescu",
    author_email="dan@cast.ai",
    description="Provides tools for SE projects (e.g. Cloud controllers).",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    test_suite='nose.collector',
    test_requires=required_for_tests,
    package_data={'': ['*.txt']},
    install_requires=required,
    version=version_from_file,
    include_package_data=True,
    keywords="cast.ai k8s eks aks gke",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Customer Service",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python"
    ],
    requires=[],
    python_requires=">=3.8"
)

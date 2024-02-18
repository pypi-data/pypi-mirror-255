"""Setup file for building distributable package."""
import os
from setuptools import setup, find_packages
from typing import Optional, List

NAME = 'trustedtwin'
version = os.getenv('TRUSTED_TWIN_CORE_VER', 'alpha')


def _read_requirements(suffix: Optional[str] = None) -> List:
    """Read requirements"""
    with open("requirements.txt", 'r') as f:
        requirements = f.read().split()

    if suffix:
        with open("requirements_{}.txt".format(suffix), 'r') as f:
            requirements.extend(f.read().split())

    return requirements


setup(
    name=NAME,
    version=version,
    url='https://gitlab.com/trustedtwin/solutions/trustedtwin-python-client',
    long_description_content_type="text/markdown",
    license='MIT',
    author='TrustedTwin',
    description='Trusted Twin Python client',
    packages=find_packages(include='*pyi'),
    long_description=open('README.md').read(),
    zip_safe=False,
    install_requires=_read_requirements(),
    package_data={
        'trustedtwin': ['*.pyi']    # includes interface files in build
    },
    extras_require={
        'async': _read_requirements('async')
    },
    python_requires='>=3.9',
)

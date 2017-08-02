import os
from setuptools import setup, find_packages
base_dir = os.path.dirname(os.path.abspath(__file__))


setup(
    name='hcipy',
    version="0.0.1",
    description="A pure python library for Bluetooth LE that has minimal dependencies.",
    #long_description="\n\n".join([
    #    open(os.path.join(base_dir, "README.md"), "r").read(),
    #]),
    long_description="A pure Python module written using only the Python standard library for interacting with the Bluetooth HCI.",
    url='https://github.com/TheBubbleworks/python-hcipy',
    author='Wayne Keenan',
    author_email='wayne@thebubbleworks.com',
    maintainer='Wayne Keenan',
    maintainer_email='wayne@thebubbleworks.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    #tests_require=tests_require,
    #test_suite="setup.test_suite",
    platforms=['Raspberry Pi', 'Linux'],
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 2',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Operating System :: POSIX',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],
)
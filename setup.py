import pathlib
import setuptools
import etrobo_python

setuptools.setup(
    name='etrobo_python',
    version=etrobo_python.__version__,
    author=etrobo_python.__author__,
    author_email='takeda@cs.tohoku-gakuin.ac.jp',
    license='MIT',
    description=pathlib.Path('README.txt').read_text().split('\n')[0],
    long_description=pathlib.Path('README.txt').read_text(),
    url='https://github.com/takedarts/etrobo-python',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    packages=setuptools.find_packages(exclude=['samples']),
    python_requires=">=3.7",
)

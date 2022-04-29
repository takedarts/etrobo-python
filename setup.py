import setuptools


setuptools.setup(
    name='etrobo_python',
    version='0.0.1',
    author='Atsushi TAKEDA',
    author_email='takeda@cs.tohoku-gakuin.ac.jp',
    license='MIT',
    description='Python framework for ET-ROBOCON 2022',
    url='https://github.com/takedarts/etrobo-python',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
)

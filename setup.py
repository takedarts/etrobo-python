import setuptools

setuptools.setup(
    name='etrobo_python',
    version='0.1',
    author='Atsushi TAKEDA',
    author_email='takeda@cs.tohoku-gakuin.ac.jp',
    license='MIT',
    description='Python middleware for ET-ROBOCON 2022',
    url='https://github.com/takedarts/etrobo-python',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    packages=setuptools.find_packages(exclude=['samples']),
    python_requires=">=3.7",
)

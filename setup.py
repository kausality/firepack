import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='firepack',
    version='1.0.0',
    author='Kaustubh Pratap Chand',
    author_email='contact@kausalitylabs.com',
    description='FirePack is a minimalist Python library for creating services, data serialization and validation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kpchand/fireservice',
    packages=setuptools.find_packages(where='firepack'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

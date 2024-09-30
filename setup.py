from setuptools import setup, find_packages

setup(
    name='models',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.1',
    ],
    description='A shared Django app for models management across multiple projects',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
)

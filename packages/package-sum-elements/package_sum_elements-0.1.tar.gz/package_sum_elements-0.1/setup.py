from setuptools import setup, find_packages

setup(
    name='package_sum_elements',
    version='0.1',
    packages=find_packages(),
    license='MIT',
    description='A package to calculate the sum of elements in a list',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Clémence SUTTER',
    keywords=['sum', 'elements', 'list'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)

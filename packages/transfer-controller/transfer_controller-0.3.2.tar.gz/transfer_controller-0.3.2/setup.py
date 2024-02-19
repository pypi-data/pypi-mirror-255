from setuptools import setup, find_packages

setup(
    name='transfer_controller',
    version='0.3.2',
    description='A module for controlling transfer sequences.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Binho LLC',
    author_email='support@binho.io',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.10',
    license='Private'
)

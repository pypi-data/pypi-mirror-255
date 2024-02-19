from setuptools import setup, find_packages

setup(
    name='XAccess',
    version='0.0.1',
    packages=find_packages(),
    license='MIT',
    description='Communication with the server using server and client',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='sphrz2324@gmail.com',
    url='https://github.com/Sepehr0Day/XAccess/',
    install_requires=[
        'requests',
        'colorama'
    ],
)

from setuptools import setup, find_packages

setup(
    name='py-url-analyzer',
    version='0.0.2',
    packages=find_packages(),
    author='Lucas Andrade',
    author_email='lafdesouza2002@gmail.com',
    description='A simple URL analyzer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/seu-usuario/seu-projeto',
    install_requires=[
        'beautifulsoup4',
        'certifi',
        'charset-normalizer',
        'idna',
        'requests',
        'soupsieve',
        'urllib3',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
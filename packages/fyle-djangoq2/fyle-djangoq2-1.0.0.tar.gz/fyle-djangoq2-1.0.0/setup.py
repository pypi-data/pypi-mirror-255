"""
Project setup file
"""
import setuptools

with open('README.rst', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='fyle-djangoq2',
    version='1.0.0',
    author='Rushikesh',
    author_email='rushikesh.t@fyle.in',
    description='Python SDK for Django Q2',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['django-q2' 'django-q', 'fyle', 'queue', 'python', 'sdk'],
    url='https://github.com/fylein/django-q2.git',
    packages=setuptools.find_packages(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)

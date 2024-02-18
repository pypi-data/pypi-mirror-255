from setuptools import setup, find_packages

setup(
    name='srpskiwordnet',
    version='0.1',
    packages=find_packages(),
    author='Petalinkar Saša',
    author_email='sasa5linkar@gmial.com',
    description='NLTK interface for Serbian Wordnet',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/sasa5linkar/Srpski-Wordenet-Python-wrapper',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests',
        'nltk',
        'pandas',
        'scikit-learn',
    ],
)
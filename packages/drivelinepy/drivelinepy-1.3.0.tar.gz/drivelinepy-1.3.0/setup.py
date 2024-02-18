from setuptools import setup, find_packages

# Read the contents of your README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drivelinepy',
    version='1.3.0',
    author='Garrett York',
    author_email='garrett@drivelinebaseball.com',
    description='A Python package for Driveline Baseball API interactions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/drivelineresearch/drivelinepy',
    packages=find_packages(),
    install_requires=[
        'requests>=2.27.1',
        'pandas>=2.0.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Corrected license classifier
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6.6',
)

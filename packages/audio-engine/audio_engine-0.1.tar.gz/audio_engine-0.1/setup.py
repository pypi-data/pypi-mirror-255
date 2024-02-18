from setuptools import setup, find_packages

setup(
    name='audio_engine',
    version='0.1',
    packages=find_packages(),
    license='MIT',
    description='This library provides common speech features for ASR including MFCCs and filterbank energies.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jession Diwangan',
    author_email='jessiondiwangan@gmail.com',
    url='https://github.com/Jss-on/audio_engine',
    install_requires=[
        # List your project dependencies here.
        # Example: 'requests>=2.19.1'
        'scipy>=1.11.1',
        'numpy>=1.23.5'
    ],
)

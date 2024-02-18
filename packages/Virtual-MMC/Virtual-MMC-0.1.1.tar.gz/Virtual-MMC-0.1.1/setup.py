from setuptools import setup, find_packages

setup(
    name='Virtual-MMC',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    author='James_Broster',
    author_email='james.broster@st-annes.ox.ac.uk',
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/James-Broster/VMMC',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

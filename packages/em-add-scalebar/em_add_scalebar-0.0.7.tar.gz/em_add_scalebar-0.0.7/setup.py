import io
from setuptools import setup,find_packages


def README():
    with io.open('README.md', encoding='utf-8') as f:
        readme_lines = f.readlines()

    return ''.join(readme_lines)
README = README()  # NOQA

setup(
    name='em_add_scalebar',
    version='0.0.7',
    python_requires='>=3.9',
    description='A package to add a scale bar to microscopy images',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://git.mpi-cbg.de/scicomp/bioimage_team/tobias_em_app_scalebar',
    author='Anthony Vega',
    author_email='vega@extern.mpi-cbg.de',
    license='BSD',
    packages=['add_scalebar'],
    include_package_data=True,
    install_requires=['numpy==1.23.5',
                      'scikit-image',
                      'matplotlib==3.7.0',
                      'microfilm==0.2.1',
                      'aicsimageio==4.14.0',
                      'opencv-python',
                      'mrcfile',
                      'Gooey>=1.0.7',
                      'ncempy==1.11.0'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
)



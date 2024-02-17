import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()
setuptools.setup(
    name='airflow_dataform_parser',
    author='Emre Celikkol',
    author_email='emrecelikkol92@gmail.com',
    version="0.1.0",
    description='Parser get dataform compile output and generates required task for airflow.',
    keywords='dataform, airflow, gcp, bigquery, pypi, package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/EmreCelikkolOredata/airflow_dataform_parser',
    project_urls={
        'Documentation': 'https://github.com/EmreCelikkolOredata/airflow_dataform_parser',
        'Bug Reports': 'https://github.com/EmreCelikkolOredata/airflow_dataform_parser',
        'Source Code': 'https://github.com/EmreCelikkolOredata/airflow_dataform_parser'
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    # install_requires=['Pillow'],
    extras_require={
        # 'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=examplepy:main',
    # You can execute `run` in bash to run `main()` in src/examplepy/__init__.py
    #     ],
    # },
)

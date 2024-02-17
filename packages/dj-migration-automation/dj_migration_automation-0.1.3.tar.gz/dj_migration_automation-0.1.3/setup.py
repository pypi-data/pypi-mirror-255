from setuptools import setup, find_packages

setup(
    name='dj_migration_automation',
    version='0.1.3',
    author='Darshit Joshi',
    author_email='darshitj@dosepack.com',
    description='this is a migration automation tool to ease the process of migration for multiple environments',
    package_data={'': ['README.md']},
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

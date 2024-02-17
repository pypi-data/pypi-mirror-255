from setuptools import setup, find_packages

setup(
    name="sawsi",
    version="7.9",
    packages=find_packages(),
    include_package_data=True,
    py_modules=['make'],
    install_requires=[
        'requests==2.31.0',
        'click~=8.1.7',
    ],
    entry_points='''
        [console_scripts]
        sawsi=make:cli
    ''',
)

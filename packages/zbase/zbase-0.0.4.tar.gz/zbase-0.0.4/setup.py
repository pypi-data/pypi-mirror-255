from setuptools import setup, find_packages

# pip install -m venv venv
# source venv/bin/activate
# pip install pytest
# venv/bin/pytest

# pip install build twine
# python -m build
# python -m twine upload --verbose -u uzoice dist/*
# pip install zbase

setup(
    name='zbase',
    version='0.0.4',
    author="Daqian",
    packages=find_packages(exclude=['tests', 'tests.*','venv']),
    zip_safe=False,
    description='foundation library of python project',
    long_description='foundation library of python project',
    license='Sci.live license',
    keywords=['sci.live'],
    install_requires=[
        'python-dotenv>=1.0.0',
        'sqlalchemy>=2.0.22',
        'redis>=5.0.1',
        'bcrypt>=4.0.1',
        'pytest>=7.4.3',
        'fastapi>=0.104.0',
        'PyJWT>=2.8.0',
        'httpx>=0.25.0',
        'PyMySQL>=1.1.0',
        'cryptography>=41.0.5',
        'minio>=7.2.0',
        'yagmail>=0.15.293'
    ],
    platforms='Independant',
    url='https://github.com/scilive/zbase',
)

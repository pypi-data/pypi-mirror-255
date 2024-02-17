from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='ShieldCipher',
    version='1.0.0',
    description='Python library for cybersecurity',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='RAH Code',
    author_email='contacto@rahcode.com',
    url='https://rah-code-dev.github.io/ShieldCipher',
    license='MIT License',
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.19.1',
    ],
    entry_points={
        'console_scripts': [
            'ShieldCipher = ShieldCipher.bin.cli:main',
        ],
    },
)

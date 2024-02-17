from setuptools import setup, find_packages

setup(
    name='covalent-api-sdk',   # Replace with the name of your package
    version='0.8.7',             # Replace with the version of your package
    license="MIT",
    # Description and long_description should contain a concise and detailed description of your project.
    description='covalent-api-sdk-py',
    long_description=open('README.md').read() + "\n",
    long_description_content_type='text/markdown',
    author='Covalenthq',          # Replace with your name
    python_requires='>=3.7',
    url='https://github.com/covalenthq/covalent-api-sdk-py/',  # Replace with the URL of your project repository
    packages=find_packages(exclude=['tests', 'tests.*']),    # Automatically find all packages in your project directory

    # Add any dependencies required by your package
    install_requires=[
        # Add your dependencies here, e.g., 'numpy>=1.18.0'
        'aiohttp',
        'pytest',
        'requests',
        'pytest-env',
        'pytest-asyncio',
        'deprecated'
    ],

    classifiers=[
        # Add classifiers to specify the audience and maturity of your package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)

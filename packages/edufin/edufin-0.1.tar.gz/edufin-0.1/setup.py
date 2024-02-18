from setuptools import setup, find_packages

setup(
    name='edufin',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy-financial',
    ],
    author='Mario Rene Salazar Torres',
    author_email='mrsalazar@outlook.com',
    description='Una biblioteca educativa de finanzas',
    url='https://github.com/msalaztor',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)

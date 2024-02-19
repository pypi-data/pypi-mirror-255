from setuptools import setup

setup(
    name='aftpy',
    version='0.0.1',
    packages=['aftpy'],
    url='https://github.com/bibhuraushan/aftpy/',
    license='MIT',
    author='Bibhuti Kumar Jha',
    author_email='bibhuraushan1@gmail.com',
    description='Python package to read and download AFTmap data.',
    keywords=['SOME', 'MEANINGFULL', 'KEYWORDS'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'matplotlib',
        'numpy',
        'astropy',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',  # Again, pick a license,
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)

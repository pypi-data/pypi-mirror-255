from setuptools import setup, find_packages

setup(
    name='luminal_rs',
    version='0.0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Deep learning at the speed of light',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[],
    url='https://github.com/jafioti/luminal',
    author='Joe Fioti',
    author_email='jafioti@gmail.com'
)

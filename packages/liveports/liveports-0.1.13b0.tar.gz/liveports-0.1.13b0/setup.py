from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='liveports',
    version='0.1.13b',
    description='Give address to your localmachine',
    author='Abhinav',
    author_email='abhinavabcd@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "brotlipy>=0.7.0",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'liveports = liveports.client:main',
        ],
    }
)

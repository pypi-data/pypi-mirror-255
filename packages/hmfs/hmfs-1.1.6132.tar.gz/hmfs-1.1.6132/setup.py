from setuptools import setup, find_packages

setup(
    name='hmfs',
    version='1.1.6132',
    packages=find_packages(),
    license="MIT",
    description='Distributed filesystem for Hamuna AI',
    long_description='Distributed filesystem for Hamuna AI with multiple third party middleware transfer points',
    long_description_content_type="text/plain",
    author='O.Push',
    author_email='opush.developer@outlook.com',
    url='https://www.hamuna.club',
    package_dir={'': '.'},
    install_requires=['minio', 'redis==4.3.4', 'paho-mqtt', 'gnsq', 'ansq', 'qiniu', 'boto', 'diskcache',
                      'httpx', 'aiofile', 'aiohttp', 'aiohttp_retry', 'aiobotocore', 'nos-python3-sdk', 'miniopy_async']
)

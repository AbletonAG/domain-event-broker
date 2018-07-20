import versioneer

from setuptools import setup, find_packages

setup(
    name='rabbit-domain-events',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Send and receive domain events via RabbitMQ',
    author='Ableton AG',
    author_email='webteam@ableton.com',
    url='https://github.com/AbletonAG/domain-events',
    license='MIT',
    packages=find_packages(),
    install_requires=["pika >= 0.10.0"],
    tests_require=["pytest >= 3.0.0", "mock"],
    zip_safe=False,
)

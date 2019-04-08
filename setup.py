import versioneer

from setuptools import setup, find_packages

# Add README as description
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='domain-event-broker',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Send and receive domain events via RabbitMQ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ableton AG',
    author_email='webteam@ableton.com',
    url='https://github.com/AbletonAG/domain-event-broker',
    license='MIT',
    packages=find_packages(),
    install_requires=["pika >= 1.0.0"],
    tests_require=["pytest >= 3.6.0"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

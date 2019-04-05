import versioneer

from setuptools import setup, find_packages

setup(
    name='domain-event-broker',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Send and receive domain events via RabbitMQ',
    author='Ableton AG',
    author_email='webteam@ableton.com',
    url='https://github.com/AbletonAG/domain-event-broker',
    license='MIT',
    packages=find_packages(),
    install_requires=["pika >= 1.0.0"],
    tests_require=["pytest >= 3.6.0", "mock"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

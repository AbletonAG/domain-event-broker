import versioneer

from setuptools import setup

setup(
    name='domain_events',
    version=versioneer.get_version(),
    cmdclass = versioneer.get_cmdclass(),
    desription='Ableton Domain Events via Rabbitmq',
    author='the Ableton web team',
    author_email='webteam@ableton.com',
    license='MIT',
    packages=['domain_events', 'tests'],
    zip_safe=False,
)

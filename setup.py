"""Python client library for IoT and Context related API management on FIWARE platform

See:
https://fiot-client.imd.ufrn.br/en/latest
https://projetos.imd.ufrn.br/FIoT-Client/fiot-client-python
"""

from setuptools import setup, find_packages

from codecs import open
import os


README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(
    name='fiotclient',
    version='0.1.0',
    description='Python client library for IoT and Context related API management on FIWARE platform',
    long_description=open(README).read(),
    url='https://projetos.imd.ufrn.br/FIoT-Client/fiot-client-python',
    author='Lucas Cristiano Calixto Dantas',
    author_email='lucascristiano27@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='fiware api iot things context development',
    py_modules=["fiotclient"],
    install_requires=['requests', 'paho-mqtt'],
    python_requires='>=2.7, <4',
)

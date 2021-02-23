from setuptools import setup, find_packages


def read(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name='xssproxy',
    version='0.0.1',
    description='Pseudo HTTP proxy for sending requests through a hooked web browser',
    long_description=read('README.md'),
    author='shiftinv',
    url='https://github.com/shiftinv/xssproxy',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=read('requirements.txt').splitlines(),
    python_requires='~=3.6',
    package_data={
        'xssproxy': ['js/*.js']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'xssproxy=xssproxy.cmdline:run'
        ]
    }
)

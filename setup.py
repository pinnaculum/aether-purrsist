from setuptools import setup


def reqs_parse(path):
    with open(path) as f:
        return f.read().splitlines()


setup(
    name='aether-purrsist',
    version='1.1.0',
    author='cipres',
    author_email='galacteek@protonmail.com',
    url='https://gitlab.com/galacteek/aether-purrsist',
    description='Tool to archive Aether boards to a static website in IPFS',
    packages=['aether_purrsist'],
    license='MIT',
    entry_points={
        'console_scripts': [
            'aether-purrsist = aether_purrsist.entrypoint:start'
        ]
    },
    install_requires=reqs_parse('requirements.txt'),
    package_data={
        'aether_purrsist': [
            '*.css'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    keywords=[
        'ipfs',
        'aether'
    ]
)

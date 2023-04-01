from setuptools import setup


def reqs_parse(path):
    with open(path) as f:
        return f.read().splitlines()


setup(
    name='aether-purrsist',
    version='1.0.0',
    description='Tool to archive Aether boards to IPFS',
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
        'Development Status :: 4 - Beta',
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

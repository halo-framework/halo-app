from io import open

from setuptools import setup

# python setup.py sdist bdist_wheel
# twine upload dist/halo_app-0.15.101.tar.gz -r pypitest

with open("README.md", "r") as h:
    long_description = h.read()

setup(
    name='halo-app',
    version='0.10.15',
    packages=['halo_app', 'halo_app.app', 'halo_app.schema','halo_app.providers', 'halo_app.providers.cloud',
              'halo_app.providers.cloud.aws', 'halo_app.providers.onprem', 'halo_app.providers.ssm',
              'halo_app.data','halo_app.infra','halo_app.domain',],
    data_files=[('schema', ['halo_app/schema/saga_schema.json'])],
    package_data={'schema': ['halo_app/schema/saga_schema.json']},
    url='https://github.com/halo-framework/halo-app',
    license='MIT License',
    author='halo-framework',
    author_email='halo-framework@gmail.com',
    description='this is the Halo framework library for domain app',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)

from io import open

from setuptools import setup

# python setup.py sdist --formats=zip
# python setup.py sdist bdist_wheel
# twine upload dist/halo_app-0.15.101.tar.gz -r pypitest

with open("README.md", "r") as h:
    long_description = h.read()

setup(
    name='halo-app',
    version='0.16.1',
    packages=['halo_app', 'halo_app.app', 'halo_app.schema','halo_app.providers', 'halo_app.providers.cloud', 'halo_app.providers.cloud.aws', 'halo_app.providers.onprem', 'halo_app.providers.ssm'],
    data_files=[('schema', ['halo_app/schema/saga_schema.json'])],
    package_data={'schema': ['halo_app/schema/saga_schema.json']},
    url='https://github.com/yoramk2/halo_flask',
    license='MIT License',
    author='yoramk2',
    author_email='yoramk2@yahoo.com',
    description='this is the Halo framework library for Flask',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)

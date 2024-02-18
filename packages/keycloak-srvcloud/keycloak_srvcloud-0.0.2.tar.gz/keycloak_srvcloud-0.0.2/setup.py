from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='keycloak_srvcloud',
  version='0.0.2',
  author='vitca64rus',
  author_email='vitca64rus@gmail.com',
  description='Lib for interacting with keycloak from srvCloud',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/VITca64rus/keycloak_srvcloud.git',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  project_urls={
    'GitHub': 'https://github.com/VITca64rus/keycloak_srvcloud.git'
  },
  python_requires='>=3.6'
)
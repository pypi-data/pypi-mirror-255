from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='bot4',
  version='0.0.1',
  author='Jeelesk',
  author_email='eywevynriimnetyiu@gmail.com',
  description='This is a module for creating bots',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='',
  packages=find_packages(),
  install_requires=['bitstring', 'cryptography'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='bot',
  project_urls={},
  python_requires='>=3.10'
)
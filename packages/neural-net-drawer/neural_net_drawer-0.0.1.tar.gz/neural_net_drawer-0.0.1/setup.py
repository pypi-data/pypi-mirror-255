from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='neural_net_drawer',
  version='0.0.1',
  author='EvgeniBondarev',
  author_email='bondareff7@gmail.com',
  description='Plugin for visual display of a neural network.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/EvgeniBondarev/Neural-Network-Drawer.git',
  packages=find_packages(),
  install_requires=['matplotlib'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='neural network display visual',
  project_urls={
    'Documentation': 'https://github.com/EvgeniBondarev/Neural-Network-Drawer.git'
  },
  python_requires='>=3.7'
)
from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='przypominacz',
  version='1.0.0',
  description='This is reminder.',
  long_description=open('README.md').read(),
  url='',  
  author='karola1902',
  author_email='karolina.czarnocka19@wp.pl',
  license='MIT', 
  classifiers=classifiers,
  keywords='reminder emails schedule',
  packages=find_packages(),
  install_requires=[] 
)
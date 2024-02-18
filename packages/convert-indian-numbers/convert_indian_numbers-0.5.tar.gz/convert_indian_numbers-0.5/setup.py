from setuptools import setup, find_packages

 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='convert_indian_numbers',
  version='0.5',
  description='Arabic Persian English Hindi Numbers is a Python library to convert numbers from-to Arabic, Indian Hindi, Persian and English.',
  long_description=open('README.md').read(),
  long_description_content_type="text/markdown",
  url='https://github.com/pranjal5215/convert_numbers',  
  author='Azwri',
  author_email='pranjal5215@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Arabic Persian English Indian Hindi Numbers Python conversion numbers from-to Arabic, Indian Hindi, Persian and English', 
  packages=find_packages(),
  install_requires=['']
)

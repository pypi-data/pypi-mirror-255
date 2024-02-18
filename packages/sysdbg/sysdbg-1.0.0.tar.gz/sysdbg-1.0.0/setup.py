from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='sysdbg',
  version='1.0.0',
  description='It wil Logs system info - Parses the Prefetch files - Recieve some other System information - And Loges Running Processes',
  author='MehranSpL',
  author_email='',
  license='MIT', 
  classifiers=classifiers,
  keywords=['system', 'prefetch', 'log', 'Process', 'debug'],
  packages=find_packages(),
  install_requires=['psutil', 'datetime' , 'wmi', 'requests'] 
)
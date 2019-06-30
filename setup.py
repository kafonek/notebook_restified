from setuptools import setup, find_packages

setup(name='notebook_restified',
      version='0.1.0',
      
      author='Matt Kafonek',
      author_email='kafonek@gmail.com',
      url='https://github.com/kafonek/notebook_restified',
            
      description='An implementation of MVC in ',
      long_description=open('README.md', encoding='utf-8').read(),
      long_description_content_type = 'text/markdown',
      
      packages=find_packages(),
      install_requires=['papermill',
                        'jupyter_client',
                        'jupyter_server',
                        'tornado',
                        'nbformat'],
      
      classifiers = [],
      license='BSD')
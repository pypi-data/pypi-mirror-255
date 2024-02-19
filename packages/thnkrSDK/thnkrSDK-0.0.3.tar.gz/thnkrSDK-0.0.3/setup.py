from setuptools import setup, find_packages

setup(
   name = 'thnkrSDK',
   version = '0.0.3',
   
   author = 'thnkrAI Inc.',
   author_email = 'contact@thnkrai.com',
   url='https://github.com/thnkrAI/thnkrSDK',
   
   description = 'Software Development Kit for connecting to the thnkrAPI',
   long_description=open('README.md').read(),
   long_description_content_type='text/markdown',
   
   packages = find_packages(),
   classifiers=[
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent',
   ],
   
   python_requires=">=3.6",
   install_requires = [
      'requests>=2.26.0',
   ],
   
   project_urls={
      'Source': 'https://github.com/thnkrAI/thnkrSDK',
      'Bug Reports': 'https://github.com/thnkrAI/thnkrSDK/issues',
   },
)
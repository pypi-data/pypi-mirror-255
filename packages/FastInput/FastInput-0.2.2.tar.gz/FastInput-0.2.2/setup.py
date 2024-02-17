from setuptools import find_packages, setup

version='0.2.2'

setup(
  name = 'FastInput',         # How you named your package folder (MyLib)
  packages = ['FastInput'],   # Chose the same as "name"
  version = version,      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A package that wrap the input function with validation',   # Give a short description about your library
  long_description=open("README.md").read(),
  long_description_content_type="text/markdown",
  author = 'Alexandre Wetzel',                   # Type in your name
  author_email = 'alexwtz@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/alexwtz/fastInput',   # Provide either the link to your github or to your website
  download_url = f"https://github.com/alexwtz/FastInput/archive/refs/tags/{version}.tar.gz",    # I explain this later on
  keywords = ['input', 'validation', 'prompt'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)

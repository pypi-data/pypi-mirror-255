from distutils.core import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'pymovie-search',               # How you named your package folder (MyLib)
  version = '1.0.7',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A pirate movie searched written in Python',   # Give a short description about your library
  long_description= long_description,
  long_description_content_type='text/markdown',
  author = 'SomedudeX',                  # Type in your name
  url = 'https://github.com/SomedudeX/PyMovie',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/SomedudeX/PyMovie/archive/refs/tags/v1.0.3.zip',    # I explain this later on
  keywords = ['movie', 'python3', 'search'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'colorama',
          'cinemagoer',
          'thefuzz',
          'requests',
          'psutil'
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
  ],
)

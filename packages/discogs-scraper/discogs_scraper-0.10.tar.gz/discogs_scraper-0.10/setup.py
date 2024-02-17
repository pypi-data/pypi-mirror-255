
from setuptools import setup

setup(
  name = 'discogs_scraper',
  packages= ['discogs_scraper'],# How you named your package folder (MyLib)
  version = '0.10',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Scrapes discogs website based on urls and then outputs csv',   # Give a short description about your library
  author = 'Casper Dancy',                   # Type in your name
  author_email = 'casperdancy@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/casperUoS/discogs-Scraper',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/casperUoS/discogs-Scraper/archive/refs/tags/0.7.tar.gz',
  keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'discogs_client',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
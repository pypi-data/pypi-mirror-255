# discogs-scraper

This is a library which currently only contains a main function. This main function
will read a URL.txt file and get release information about that release and output
it into a file name output.csv

This is not a feature complete version and there will more updates coming


## Installation

Install [the client from PyPI](https://pypi.org/project/python3-discogs-client/)
using your favorite package manager.

```sh
$ pip3 install discogs-scraper
```

## Quickstart

### To Run Main

Run the below in a terminal which contains "URL.txt", where the file contains a 
new URL of a discog release on each line

Note that the URL must contain "release", not "master release"

```python
>>> import discogs_scraper
>>> discogs_scraper.main()
```

To run straight fr

## Contributing

1. Fork this repo
2. Create a feature branch
3. Open a pull-request

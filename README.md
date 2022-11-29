# Regulation Public Comments Monitor

This is a quick and simple example of using the regulations.gov API to create an RSS feed of public comments on various dockets (e.g. https://www.regulations.gov/docket/EPA-HQ-OPPT-2020-0493). It’s a pretty simple Python script that runs on a schedule using GitHub Actions, and outputs a set of RSS feeds (one for each docket it monitors).


## Setup

This project uses [Poetry](https://python-poetry.org/). To set it up:

1. Make sure you have Poetry installed. See https://python-poetry.org/docs/ for instructions.

2. Clone this repository.

3. Run `poetry install` to create a virtual environment and install the dependencies into it.

    ```sh
    $ poetry install
    ```

4. Set the `REGULATIONS_GOV_API_KEY` environment variable. If you need an API key, see the instructions for getting one at https://open.gsa.gov/api/regulationsgov/#getting-started.

    ```sh
    $ export REGULATIONS_GOV_API_KEY='YOUR KEY HERE'
    ```

5. Run the `docket-comments.py` program! Each argument is a docket to make an RSS feed for. For example:

    ```sh
    $ poetry run python docket-comments.py 'EPA-HQ-OAR-2021-0668' 'EPA-HQ-OPPT-2020-0493'
    ```

    The resulting RSS feeds will be written to `./out/<docket-id>.rss`.


## Roadmap

This is a quick and simple demo! If this is useful, it’ll get moved the EDGI’s GitHub account and potentially expanded to support more complex usage, more dockets, organizational partners, etc.


## License

Regulation Public Comments Monitor is open source software. It is (c) 2022 Rob Brackett and licensed under the BSD license. The full license text is in the LICENSE file.

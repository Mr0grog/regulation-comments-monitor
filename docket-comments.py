from os import getenv
from pathlib import Path
from sys import argv, exit, stderr
from regulation_comments_monitor import create_feed


def main():
    api_key = getenv('REGULATIONS_GOV_API_KEY')
    if not api_key:
        print(
            'The `REGULATIONS_GOV_API_KEY` environment variable must be set!',
            file=stderr
        )
        exit(1)

    docket_ids = argv[1:]
    out_folder = Path('./out')
    out_folder.mkdir(exist_ok=True)

    for docket_id in docket_ids:
        feed_path = out_folder / f'{docket_id}.rss'
        print(f'Creating RSS for {docket_id} at {feed_path}...')

        feed = create_feed(api_key, docket_id)
        with feed_path.open('wb') as file:
            file.write(feed.format_rss())


if __name__ == '__main__':
    main()

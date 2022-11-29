from collections import defaultdict
from datetime import datetime, timedelta, timezone
import dateutil.parser
from regulation_comments_monitor.regulations_gov import RegulationsGovApi
from regulation_comments_monitor.feed import NewsFeed, NewsItem


def docket_view_url(docket_id):
    return f'https://www.regulations.gov/docket/{docket_id}'


def comment_view_url(comment_id):
    return f'https://www.regulations.gov/comment/{comment_id}'


def create_feed(api_key, docket_id):
    client = RegulationsGovApi(api_key)

    docket = client.get_docket(docket_id)
    feed = NewsFeed(title=f'Docket {docket["id"]} Comments',
                    home_page_url=docket_view_url(docket_id),
                    description=f'Public comments on regulations.gov docket {docket["id"]}: {docket["attributes"]["title"]}')

    by_date = defaultdict(list)
    by_modified_date = defaultdict(list)
    dates = set()
    for comment in client.list_docket_comments(docket_id):
        # print(f'{index + 1}: {comment}')
        url = comment_view_url(comment['id'])
        posted_at = dateutil.parser.parse(comment['attributes']['postedDate'])
        modified_at = dateutil.parser.parse(comment['attributes']['lastModifiedDate'])
        comment['posted_at'] = posted_at
        comment['modified_at'] = modified_at

        posted_date = posted_at.strftime('%Y-%m-%d')
        modified_date = modified_at.strftime('%Y-%m-%d')
        by_date[posted_date].append(comment)
        dates.add(posted_date)
        # FIXME: it looks like every comment generally has a modified date that
        # is at least the next day after the posted date (maybe there's a
        # manual approval process or some workflow that takes a day). That
        # unfortunately means every comment gets listed on two days, even if it
        # was never actually updated by its author. Not sure we can do anything
        # interesting with this info.
        #
        # if modified_date != posted_date:
        #     by_modified_date[modified_date].append(comment)
        #     dates.add(modified_date)

    for date in dates:
        posted_count = 0
        modified_count = 0
        posted_items = []
        modified_items = []
        if date in by_date:
            posted_items = sorted(by_date[date], key=lambda x: x['posted_at'])
            posted_count = len(posted_items)
        # if date in by_modified_date:
        #     modified_items = sorted(by_modified_date[date], key=lambda x: x['modified_at'])
        #     modified_count = len(modified_items)

        title = f'{posted_count} New Comments on Docket {docket_id} on {date}'
        # if posted_count == 0:
        #     title = f'{modified_count} Updated Comments on Docket {docket_id} on {date}'

        date_value = datetime.strptime(date, '%Y-%m-%d')
        date_value.replace(tzinfo=timezone.utc)
        next_date = (date_value + timedelta(days=1)).strftime('%Y-%m-%d')
        url = f'https://www.regulations.gov/docket/{docket_id}/comments?postedDateFrom={date}&postedDateTo={next_date}'

        new_comment_list = [f'<li><a href="{comment_view_url(comment["id"])}">{comment["attributes"]["title"]}</a></li>'
                            for comment in posted_items]
        # modified_comment_list = [f'<li><a href="{comment_view_url(comment["id"])}">{comment["attributes"]["title"]}</a></li>'
        #                          for comment in modified_items]

        # summary = (f'<p>On {date}, <strong>{posted_count}</strong> new public '
        #            f'comments were posted and <strong>{modified_count}</strong> '
        #            f'comments were updated for docket {docket_id} '
        #            f'({docket["attributes"]["title"]}).<p>'
        #            f'\n<h2>{posted_count} New Comments</h2>'
        #            f'\n<ul>{"".join(new_comment_list)}\n</ul>'
        #            f'\n<h2>{modified_count} Updated Comments</h2>'
        #            f'\n<ul>{"".join(modified_comment_list)}\n</ul>')
        summary = (f'<p>On {date}, <strong>{posted_count}</strong> new public '
                   f'comments were posted for docket '
                   f'<a href="{docket_view_url(docket_id)}">{docket_id} '
                   f'({docket["attributes"]["title"]})</a>.<p>'
                   f'\n<h2>{posted_count} New Comments</h2>'
                   f'\n<ol>{"".join(new_comment_list)}\n</ol>')

        item = NewsItem(id=f'urn:regulations.gov/comments/{date}',
                        url=url,
                        title=title,
                        date_published=date_value,
                        summary=summary)
        feed.append(item)

    return feed

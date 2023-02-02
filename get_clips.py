import requests
import datetime
import os

from cliputil import get_clips


def pick_best_url_from_list(urls):
    cuts_clips = [url for url in urls if url.startswith(
        "https://mlb-cuts-diamond.mlb.com/")]
    if len(cuts_clips) > 0:
        hq_cuts_clips = [url for url in cuts_clips if "16000K" in url]
        if len(hq_cuts_clips) > 0:
            return hq_cuts_clips[0]
        else:
            return cuts_clips[0]
    else:
        return urls[0]


def get_best_url_for_play(play):
    # haven't seen an instance in which there's more than one mediaPlayback
    media_playback = play["mediaPlayback"][0]
    feeds = media_playback["feeds"]
    for feed in feeds:
        playbacks = feed["playbacks"]
        feed_urls = []
        for playback in playbacks:
            if playback['url'].endswith("mp4"):
                feed_urls.append(playback['url'])

        if len(feed_urls) > 0:
            return pick_best_url_from_list(feed_urls)


def fetch_clips(target_dir=None):

    if target_dir is None:
        target_dir = f"./cliptool-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    res = get_clips(batter_id=664034, hit_result="Strikeout",
                    limit=10, start_date="2022-08-01", end_date="2022-08-31")

    for play in res:

        url = get_best_url_for_play(play)

        # download the clip
        r = requests.get(url, stream=True, headers={
            # add referer header to avoid getting html instead of mp4
            'Referer': 'https://www.mlb.com/'
        })

        filename = os.path.join(
            target_dir, f"{play['gameDate']}_{play['mediaPlayback'][0]['slug']}.mp4")

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "wb") as f:
            f.write(r.content)


fetch_clips()

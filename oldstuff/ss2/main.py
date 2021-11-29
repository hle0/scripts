#!/usr/bin/python3

lock_file = '/tmp/ss2.lock'
subreddits_file = '/mnt/e/randomcode2/ss2/subreddits.txt'
ts_file = '/mnt/e/randomcode2/ss2/ts'
logs_file = '/mnt/e/randomcode2/ss2/ss2.log'
save_dir = '/mnt/e/randomcode2/ss2/data/'

def log(*args):
    msg = ' '.join(str(arg) for arg in args) + '\n'
    with open(logs_file, 'a') as f:
        f.write(msg)

import os
import sys
import time

import praw

import credentials

def main():
    if not ((len(sys.argv) > 1) and (sys.argv[1] == 'clear-lock')):
        if os.path.exists(lock_file):
            log('tried to run, but lock file existed.')
            sys.exit(1)
        else:
            f = open(lock_file, 'w+')
            e = None
            try:
                _main()
            except Exception as err:
                e = err
            finally:
                os.remove(lock_file)
                if e is not None:
                    raise e
    else:
        if os.path.exists(lock_file):
            os.remove(lock_file)
            log('cleared the lock file')
        sys.exit(0)

def write_time(f, t):
    f.write(str(int(t)))

def _main():
    if not os.path.exists(ts_file):
        with open(ts_file, 'w+') as f:
            write_time(f, time.time() - 86400)
    
    with open(ts_file, 'r') as f:
        ts = int(f.read())
    with open(ts_file, 'w') as f:
        write_time(f, time.time())
    latest_ts = int(time.time())

    reddit = praw.Reddit(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        username=credentials.username,
        password=credentials.password,
        user_agent=credentials.user_agent
    )

    with open(subreddits_file, 'r') as f:
        for line in f:
            if (line is not None) and (not line.isspace()) and (not line.strip().startswith('#')):
                sr = line.strip()
                log('checking subreddit', sr)
                try:
                    with open(os.path.join(save_dir, sr) + '.txt', 'a') as g:
                        for url in download(reddit, sr, ts, latest_ts):
                            g.write(url + '\n')
                except Exception as e:
                    log('got an error', repr(e))

def download(reddit: praw.Reddit, sr: str, ts: int, latest: int):
    subreddit: praw.models.Subreddit = reddit.subreddit(sr)
    post: praw.models.Submission
    for post in subreddit.new():
        if post.created_utc > latest:
            continue
        if post.created_utc < ts:
            break
        if post.is_self:
            continue
        log('got post from subreddit', sr, 'titled', post.title)
        yield str(post.url)

if __name__ == "__main__":
    main()
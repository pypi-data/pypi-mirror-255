
# standard
import json
import time
import calendar
import concurrent.futures
from datetime import datetime
from rich.console import Console

# third-party
import urllib3

# local
from .util import MetalArchivesDirectory, get_json, normalize_keyword_casing
from ..interface import AlbumProfile, ReleasePage, ReleasePages


class AlbumError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __repr__(self):
        return self.__name__ + f'<{self.status_code}>'



class Album:

    @staticmethod
    def get_profile(profile_url: str) -> AlbumProfile:
        while True:
            response = urllib3.request('GET', profile_url)
            status_code = response.status

            if status_code == 520:
                time.sleep(30)
                continue

            elif status_code != 200:
                raise AlbumError(status_code)

            break

        return AlbumProfile(profile_url, response.data)
    
    @staticmethod
    def _get_profile_thread(profile_url: str) -> tuple[AlbumProfile | None, str]:
        response = urllib3.request('GET', profile_url)
        status_code = response.status

        if status_code == 520:
            return None, profile_url

        elif status_code != 200:
            raise AlbumError(status_code)

        return AlbumProfile(profile_url, response.data), profile_url
    
    @classmethod
    def get_profiles(cls, profile_urls: list[str], segment_size=16, 
                     depth=0, max_depth=3) -> list[AlbumProfile]:
        profile_urls_swap = list()
        profiles = list()
        profile_urls_len = len(profile_urls)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                # feed the beast
                album_futures = (executor.submit(cls._get_profile_thread, url) 
                                 for url in profile_urls[segment_start:segment_end])

                # examine the remains
                for future in concurrent.futures.as_completed(album_futures):
                    profile, profile_url = future.result()
                    if profile is None:
                        profile_urls_swap.append(profile_url)
                    else:
                        profiles.append(profile)
        
        # if there's any left, throw them back into the pit
        if len(profile_urls_swap) > 0 and max_depth > depth:
            profiles += cls.get_profiles(profile_urls_swap,
                                         segment_size=segment_size,
                                         depth=depth + 1, 
                                         max_depth=max_depth)
        
        return profiles

    @staticmethod
    def get_upcoming(echo=0, page_size=100, wait=.1, verbose=False) -> ReleasePage:
        console = Console()
        data = ReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        while True:
            endpoint = MetalArchivesDirectory.upcoming_releases(echo, record_cursor, page_size)
            
            if verbose:
                console.log('GET', endpoint)

            response = get_json(endpoint, timeout)
            releases = ReleasePage(**normalize_keyword_casing(response))

            data.append(releases)

            record_cursor += page_size
            echo += 1

            if releases.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()

    @staticmethod
    def get_range(range_start: datetime, range_stop: datetime | None = None,
                  echo=0, page_size=100, wait=.1, verbose=False) -> ReleasePage:

        console = Console()
        data = ReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        range_stop_str = range_stop.strftime('%Y-%m-%d') if range_stop is not None else '0000-00-00'

        while True:
            endpoint = MetalArchivesDirectory.upcoming_releases(echo, record_cursor, page_size,
                                                                range_start.strftime('%Y-%m-%d'),
                                                                range_stop_str)
            
            if verbose:
                console.log('GET', endpoint.replace(MetalArchivesDirectory.METAL_ARCHIVES_ROOT, ''))

            response = get_json(endpoint, timeout)
            releases = ReleasePage(**normalize_keyword_casing(response))

            data.append(releases)

            record_cursor += page_size
            echo += 1

            if releases.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()
    
    @classmethod
    def get_month(cls, year, month) -> ReleasePage:
        first_day, last_day = calendar.monthrange(year, month)
        month_albums = cls.get_range(datetime(year, month, first_day), 
                                     datetime(year, month, last_day))
        
        return month_albums

    @classmethod
    def get_all(cls):
        year_range = range(1970, datetime.now().year + 2)
        months = [(year, month) 
                  for month in range(1, 13) 
                  for year in year_range]
        
        release_pages = ReleasePages(cls.get_month(*n) for n in months)

        return release_pages.combine()


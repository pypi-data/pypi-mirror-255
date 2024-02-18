import time
import concurrent.futures

import urllib3
from rich.console import Console

from .util import MetalArchivesDirectory
from ..interface import BandProfile, BandExternalLinks, SearchResults


class BandError(Exception):
    def __init__(self, status_code, url):
        self.status_code = status_code
        self.url = url

    def __repr__(self):
        return self.__name__ + f'<{self.status_code}: {self.url}>'


class Band:

    @staticmethod
    def search_profile(band_name: str, **kwargs) -> BandProfile:
        query_str = MetalArchivesDirectory.search_query(band_name=band_name, **kwargs)
        search_url = MetalArchivesDirectory.METAL_ARCHIVES_SEARCH + '?' + query_str

        while True:
            response = urllib3.request('GET', search_url)
            status_code = response.status

            if status_code == 520:
                time.sleep(30)
                continue

            elif status_code != 200:
                raise BandError(status_code, search_url)
            
            break

        return SearchResults(search_url, response.data)
    
    @staticmethod
    def get_profile(profile_url: str) -> BandProfile:
        while True:
            response = urllib3.request('GET', profile_url)
            status_code = response.status

            if status_code == 520:
                time.sleep(30)
                continue

            elif status_code == 429:
                time.sleep(10)
                continue

            elif status_code != 200:
                raise BandError(status_code, profile_url)
            
            break

        return BandProfile(profile_url, response.data)
    
    @staticmethod
    def get_profile_links(metallum_id: int) -> BandExternalLinks:
        links_url = MetalArchivesDirectory.links_query(metallum_id)
        while True:
            response = urllib3.request('GET', links_url)
            status_code = response.status

            if status_code == 520:
                time.sleep(30)
                continue

            elif status_code != 200:
                raise BandError(status_code, links_url)
            
            break

        return BandExternalLinks(metallum_id, response.data)
    
    @staticmethod
    def _get_profiles_thread(profile_url: str, verbose=False) -> tuple[BandProfile | None, str]:
        console = Console()
        
        response = urllib3.request('GET', profile_url)
        status_code = response.status

        if verbose:
            relative_url = profile_url.replace(MetalArchivesDirectory.METAL_ARCHIVES_ROOT, '')
            console.log((f'GET {relative_url}'))

        if status_code == 520:
            return None, profile_url

        elif status_code != 200:
            raise BandError(status_code, profile_url)

        return BandProfile(profile_url, response.data), profile_url

    @staticmethod
    def _get_links_thread(metallum_id: int, verbose=False) -> tuple[BandProfile | None, str]:
        links_url = MetalArchivesDirectory.links_query(metallum_id)
        
        console = Console()
        
        response = urllib3.request('GET', links_url)
        status_code = response.status

        if verbose:
            relative_url = links_url.replace(MetalArchivesDirectory.METAL_ARCHIVES_ROOT, '')
            console.log((f'GET {relative_url}'))

        if status_code == 520:
            return None, links_url

        elif status_code != 200:
            raise BandError(status_code, links_url)

        return BandExternalLinks(metallum_id, response.data), links_url

    @classmethod
    def get_profiles(cls, profile_urls: list[str], segment_size=8, 
                     depth=0, max_depth=3, verbose=False, wait=3) -> list[BandProfile]:

        console = Console()
        profile_urls_swap = list()
        profiles = list()
        profile_urls_len = len(profile_urls)

        if verbose:
            console.log(f'Executing wave {depth} | {profile_urls_len} profiles')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                band_futures = list()
                for url in profile_urls[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls._get_profiles_thread, url, verbose=verbose)
                        band_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(band_futures):
                    profile, profile_url = future.result()
                    if profile is None:
                        profile_urls_swap.append(profile_url)
                    else:
                        profiles.append(profile)

        # if there's any left, throw them back into the pit
        if len(profile_urls_swap) > 0 and max_depth > depth:
            if verbose:
                console.log((f'Wave {depth} completed with errors'))

            profiles += cls.get_profiles(profile_urls_swap, segment_size=segment_size,
                                         depth=depth + 1, max_depth=max_depth)
        
        return profiles
    
    @classmethod
    def get_profiles_links(cls, metallum_ids: list[int], segment_size=8, 
                           depth=0, max_depth=3, verbose=False, wait=3) -> list[BandExternalLinks]:

        console = Console()
        link_url_swap = list()
        links = list()
        metallum_ids_count = len(metallum_ids)

        if verbose:
            console.log(f'Executing wave {depth} | {metallum_ids_count} link pages')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, metallum_ids_count + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, metallum_ids_count)

                band_futures = list()
                for url in metallum_ids[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls._get_links_thread, url, verbose=verbose)
                        band_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(band_futures):
                    profile, profile_url = future.result()
                    if profile is None:
                        link_url_swap.append(profile_url)
                    else:
                        links.append(profile)

        # if there's any left, throw them back into the pit
        if len(link_url_swap) > 0 and max_depth > depth:
            if verbose:
                console.log((f'Wave {depth} completed with errors'))

            links += cls.get_profiles(link_url_swap, segment_size=segment_size,
                                      depth=depth + 1, max_depth=max_depth)
        
        return links

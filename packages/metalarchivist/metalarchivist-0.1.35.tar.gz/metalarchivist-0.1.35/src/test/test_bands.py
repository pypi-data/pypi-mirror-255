
import os
import sys
import json
import unittest
import importlib.util
from types import ModuleType
from enum import Enum

from configparser import ConfigParser


class Submodule(Enum):
    MODULE = 'metalarchivist', './src/metalarchivist/__init__.py'
    EXPORT = 'metalarchivist.export', './src/metalarchivist/export/__init__.py'
    IFACE = 'metalarchivist.interface', './src/metalarchivist/interface/__init__.py'


def run_test_cases():
    unittest.main(argv=[''], verbosity=2)


def prepare_submodule(submodule: Submodule) -> ModuleType:
    submodule_name, submodule_path = submodule.value
    spec = importlib.util.spec_from_file_location(submodule_name, submodule_path)
    if spec is not None and spec.loader is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[submodule_name] = module
        spec.loader.exec_module(module)
    else:
        raise ImportError(f'could not load {submodule_name}')

    return module


def load_module():
    config = ConfigParser()
    config.read_dict({'unittests': {'OUTPUTDIR': './'}})
    config.read('metallum.cfg')

    metalarchivist = prepare_submodule(Submodule.MODULE)
    interface = prepare_submodule(Submodule.IFACE)
    export = prepare_submodule(Submodule.EXPORT)

    return metalarchivist, interface, export, config


class TestBands(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()

    def test_band_search(self):

        query_str = self.export.MetalArchivesDirectory.search_query('bathory')
        expected_query_str = ''


    def test_band_report(self):

        bands = self.metalarchivist.get_bands(['https://www.metal-archives.com/bands/Furia/23765',
                                               'https://www.metal-archives.com/bands/Cult_of_Fire/3540334368',
                                               'https://www.metal-archives.com/bands/Urfaust/19596',
                                               'https://www.metal-archives.com/bands/A_Forest_of_Stars/115504',
                                               'https://www.metal-archives.com/bands/Burzum/88',
                                               'https://www.metal-archives.com/bands/Mayhem/67',
                                               'https://www.metal-archives.com/bands/Satanic_Warmaster/989'])

        self.assertIsInstance(bands, list)
        
        output_path = os.path.join(self.config['unittests']['OUTPUTDIR'], 'test-bands.json')
        json.dump(bands, open(output_path, 'w'))

    def test_band_profile(self):
        self.assertIn('Band', dir(self.export))

        band = self.export.Band.get_profile('https://www.metal-archives.com/bands/Furia/23765')
        self.assertEqual(band.name, 'Furia')
        self.assertEqual(band.metallum_id, 23765)

        self.assertIsNotNone(band.themes)
        self.assertIsInstance(band.themes, self.interface.Themes)
        self.assertIsInstance(band.genres, self.interface.Subgenres)

    def test_band_profiles(self):
        self.assertIn('Band', dir(self.export))

        bands = self.export.Band.get_profiles(['https://www.metal-archives.com/bands/Furia/23765',
                                               'https://www.metal-archives.com/bands/Cult_of_Fire/3540334368',
                                               'https://www.metal-archives.com/bands/Urfaust/19596',
                                               'https://www.metal-archives.com/bands/A_Forest_of_Stars/115504',
                                               'https://www.metal-archives.com/bands/Burzum/88',
                                               'https://www.metal-archives.com/bands/Mayhem/67',
                                               'https://www.metal-archives.com/bands/Satanic_Warmaster/989'])

        self.assertEqual(len(bands), 7)

    def test_band_links(self):
        band_links = self.export.Band.get_profile_links(19596)

        self.assertIn('Bandcamp', band_links.links)
        self.assertIn('Deezer', band_links.links)
        self.assertIn('Instagram', band_links.links)
        self.assertIn('Spotify', band_links.links)
        self.assertIn('Tidal', band_links.links)
        self.assertIn('Amazon', band_links.links)
        self.assertIn('Apple Music', band_links.links)
        self.assertIn('BigCartel', band_links.links)
        self.assertIn(b'V\xc3\x83\xc2\xa1n Records'.decode(), band_links.links)

    def test_band_themes(self):
        ...

if __name__ == '__main__':
    run_test_cases()

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
    module = importlib.util.module_from_spec(spec)
    sys.modules[submodule_name] = module
    spec.loader.exec_module(module)

    return module


def load_module():
    config = ConfigParser({'unittests': {'OUTPUTDIR': './'}})
    config.read('metallum.cfg')

    metalarchivist = prepare_submodule(Submodule.MODULE)
    interface = prepare_submodule(Submodule.IFACE)
    export = prepare_submodule(Submodule.EXPORT)

    return metalarchivist, interface, export, config


class TestGenres(unittest.TestCase):
    metalarchivist, interface, export, config = load_module()

    def test_genres_pages(self):
        target_genre = self.interface.Genre.POWER

        genre_bands = self.export.Genre.get_genre(target_genre)
        self.assertIsNotNone(genre_bands)
        self.assertIsInstance(genre_bands, self.interface.GenrePage)
        self.assertIsInstance(genre_bands.data, list)
        self.assertIsInstance(genre_bands.data[0], self.interface.BandGenre)
        self.assertEqual(genre_bands.data[0].genre, target_genre.value)

        genre_json = genre_bands.to_json()
        self.assertIsInstance(genre_json, list)
        self.assertIsInstance(genre_json[0], dict)

    def test_genres_report(self):
        genres = self.export.Genre.get_genres()
        
        genres_json = genres.to_json()
        self.assertIsInstance(genres_json, list)
        self.assertIsInstance(genres_json[0], dict)

        output_path = os.path.join(self.config['unittests']['OUTPUTDIR'], 'test-genres.json')
        json.dump(genres.to_json(), open(output_path, 'w'))

    def test_genres(self):

        genres = self.interface.Subgenres('Black Metal/Black \'n\' Roll')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 2)
        self.assertEqual(genres.clean_genre, 'Black, Black\'n\'Roll')

        genres = self.interface.Subgenres('Drone/Doom Metal (early); Psychedelic/Post-Rock (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Doom, Drone, Post-Rock, Psychedelic')

        genres = self.interface.Subgenres('Progressive Doom/Post-Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Doom, Post-Metal, Progressive')

        genres = self.interface.Subgenres('Black Death Metal/Grindcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Black, Death, Grind, Metalcore')

        genres = self.interface.Subgenres('Black Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Black')

        genres = self.interface.Subgenres('Progressive Death/Black Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Black, Death, Progressive')

        genres = self.interface.Subgenres('Epic Black Metal')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 2)
        self.assertEqual(genres.clean_genre, 'Black, Epic')

        genres = self.interface.Subgenres('Various (early); Atmospheric Black Metal, Ambient (later)')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Various, Ambient, Atmospheric, Black')

        genres = self.interface.Subgenres('Symphonic Gothic Metal with Folk influences')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 3)
        self.assertEqual(genres.clean_genre, 'Folk, Gothic, Symphonic')

        genres = self.interface.Subgenres('Dungeon Synth')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Dungeon-Synth')

        genres = self.interface.Subgenres('Symphoniccore, Melodiccore, Grindcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Grind, Melodic, Metalcore, Symphonic')
    
        genres = self.interface.Subgenres('Metalcore')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 1)
        self.assertEqual(genres.clean_genre, 'Metalcore')

        genres = self.interface.Subgenres('Prog Rock, Post-Black')
        self.assertIsNotNone(genres)
        self.assertEqual(len(genres.phases), 4)
        self.assertEqual(genres.clean_genre, 'Black, Post-Metal, Progressive, Rock')

if __name__ == '__main__':
    run_test_cases()

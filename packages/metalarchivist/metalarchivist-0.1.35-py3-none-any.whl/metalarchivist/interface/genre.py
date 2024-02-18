import re
from enum import StrEnum, auto, unique
from dataclasses import dataclass, field

@unique
class SubgenrePeriod(StrEnum):
    EARLY = auto()
    MID = auto()
    LATER = auto()
    ALL = auto()
    ERROR = auto()

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls._value2member_map_
    
    @classmethod
    def get(cls, value: str, default):
        try:
            return cls[value]
        except KeyError:
            return default


@unique
class Genre(StrEnum):
    """ based on the representation of each in a metalarchives URL

        replace `auto()` with a string literal, should an error occur
    """
    BLACK = auto()
    DEATH = auto()
    DOOM = auto()
    AVANTGARDE = auto()
    FOLK = auto()
    GOTHIC = auto()
    GRIND = auto()
    GROOVE = auto()
    HEAVY = auto()
    METALCORE = auto()
    POWER = auto()
    PROG = auto()
    SPEED = auto()
    ORCHESTRAL = auto()
    THRASH = auto()


class GenreJunk(StrEnum):
    METAL = auto()
    ELEMENTS = auto()
    INFLUENCES = auto()
    MUSIC = auto()
    AND = auto()
    WITH = auto()

    @classmethod
    def has_value(cls, value) -> bool:
        return value.lower() in cls._value2member_map_
    

@dataclass(frozen=True)
class SubgenrePhase:
    name: str
    period: SubgenrePeriod = field(default=SubgenrePeriod.ALL)


class SubgenreRules:

    junk = {r'\b \'n\' \b': '\'n\'',
            r'\u200b': '',
            chr(1089): chr(99),
            r'(\w)\(': r'\g<1> (',
            r'\)\/? ': r'); ',
            r' \- ': ' '}

    substitutions = {r'(dungeon) (synth)': r'\g<1>-\g<2>',
                     r'\b(hard) (rock)\b': r'\g<1>-\g<2>',
                     r'\b(new) (wave)\b': r'\g<1>-\g<2>',
                     r'\b(synth) (pop)\b': r'\g<1>-\g<2>',
                     r'\b([a-z]+)core\b': r'\g<1> Metalcore',
                     r'\bprog\b': r'Progressive',
                     r'\bpost-black\b': r'Post-Metal Black',
                     r'\bblackened\b': r'Black',
                     r'\bcore\b': r'Hardcore'}


@dataclass
class Subgenres:
    """ Handle genres specified in text assuming 
        the conventions applied by metal-archives.com
        
        Phases: separated by semicolons (;), denotes a change
            in a bands sound over a series of periods wrapped in
            parentheses, *early*, *mid*, and *later*. See `GenrePhase`.

            *e.g* Doom Metal (early); Post-Rock (later)

        Multiples: A slash (/) indicates that a band fits within
            multiple genres. Phases are subdivided into multiples,
            where applicable. Bands without phases will likewise
            contain multiples.

            *e.g* Drone/Doom Metal (early); Psychedelic/Post-Rock (later),
                Progressive Death/Black Metal

        Modifiers: A genre can be modified into a variant with descriptive
            text, delimited by a space ( ).

            *e.g* Progressive Death Metal

        Junk: Words that are largely uninformative can be removed, the most
            common being "Metal". See `GenreJunk`.

            *e.g* Symphonic Gothic Metal with Folk influences
    """

    full_genre: str
    clean_genre: str = field(init=False)
    phases: list[SubgenrePhase] = field(init=False)

    def __post_init__(self):
        
        clean_genre = self.full_genre
        for pattern, substitution in SubgenreRules.junk.items():
            clean_genre = re.sub(pattern, substitution, clean_genre, flags=re.IGNORECASE)

        for pattern, substitution in SubgenreRules.substitutions.items():
            clean_genre = re.sub(pattern, substitution, clean_genre, flags=re.IGNORECASE)

        phases = clean_genre.split(';')

        # strip and use regex to parse genre phase components
        phases = list(map(self._parse_phase, map(str.lstrip, phases)))

        # explode strings into multiple records by character
        phases = self._explode_phases_on_delimiter(phases, '/')
        phases = self._explode_phases_on_delimiter(phases, ',')

        # remove meaningless text
        phases = self._scrub_phases_of_junk(phases)

        # convert genres that appear in all phases to a single ALL record
        phases = self._collapse_recurrent_phases(phases)

        self.phases = phases = list(set(phases))
        sorted_genres = sorted(phases, key=self._phase_sort_key)
        self.clean_genre = ', '.join(map(lambda n: n.name, sorted_genres))

    @staticmethod
    def _phase_sort_key(phase: SubgenrePhase):
        return (SubgenrePeriod._member_names_.index(phase.period.name), phase.name)

    @staticmethod
    def _collapse_recurrent_phases(phases: list[SubgenrePhase]) -> list[SubgenrePhase]:
        total_phases = len(set(map(lambda n: n.period, phases)))

        phase_counts = dict()
        for phase in phases:
            try:
                phase_counts[phase.name] += 1
            except KeyError:
                phase_counts[phase.name] = 1

        consistent_genres = set(g for g, c in phase_counts.items() if c == total_phases)
        collapsed_phases = list(map(SubgenrePhase, consistent_genres)) 
        collapsed_phases += list(filter(lambda p: p.name not in consistent_genres, phases))

        return collapsed_phases

    @staticmethod
    def _scrub_phases_of_junk(phases: list[SubgenrePhase]) -> list[SubgenrePhase]:
        def scrub(phase):
            return [SubgenrePhase(p, phase.period)
                    for p in phase.name.split(' ')
                    if not GenreJunk.has_value(p)]
        
        return sum(list(map(scrub, phases)), [])

    @staticmethod
    def _explode_phases_on_delimiter(phases: list[SubgenrePhase], delimiter: str) -> list[SubgenrePhase]:
        def explode(phase):
            return [SubgenrePhase(n.strip(), phase.period) for n in phase.name.split(delimiter)]
            
        return sum(list(map(explode, phases)), [])

    @staticmethod
    def _parse_phase(phase: str) -> SubgenrePhase:
        phase_match = re.compile(r'^(?P<name>.*?)(\((?P<period>[\w\/\, ]+)\))?$').match(phase)
        if phase_match is None:
            raise ValueError

        period_text = phase_match.group('period')

        if period_text is not None:
            period = SubgenrePeriod.get(period_text.upper(), SubgenrePeriod.ERROR)
        else:
            period = SubgenrePeriod.ALL

        phase_name = phase_match.group('name')

        return SubgenrePhase(phase_name, period)
    
    def to_dict(self) -> dict:
        phases = [dict(name=p.name.lower(), period=p.period.value) for p in self.phases]
        return dict(genre=self.clean_genre.lower(), genre_phases=phases)

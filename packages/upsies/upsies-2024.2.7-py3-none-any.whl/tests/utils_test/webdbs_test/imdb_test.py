from itertools import zip_longest

import pytest

from upsies.utils.types import ReleaseType
from upsies.utils.webdbs import Query, SearchResult, imdb


@pytest.fixture
def api():
    return imdb.ImdbApi()


ids = {
    'pygmalion': 'tt0190673',                       # Actor name contains "&apos;"
    '1899': 'tt9319668',                            # Series with digit-only title
    '1984': 'tt0048918',                            # Movie with digit-only title
    '3 days to kill': 'tt2172934',                  # Movie title starts with number
    'adu': 'tt9616700',                             # Movie title contains special character (Adú)
    'the nest': 'tt0280990',                        # Non-English AKA contains special character (guêpes)
    'february': 'tt3286052',                        # English AKA
    'ao': 'tt1526578',                              # No English AKA available
    'wind in the willows': 'tt0192802',             # TV movie
    'benders big score': 'tt0471711',               # Video
    'elephant': 'tt0097270',                        # TV movie
    'kung fury': 'tt3472226',                       # Short
    'the forest': 'tt6560040',                      # TV miniseries
    'the bridge': 'tt1733785',                      # Series
    'the bridge s02e03': 'tt3146200',               # Episode
    'aftermath': 'tt0896516',                       # Video, no cast list
    'wingwall auditions': 'tt0253248',              # No description
    'the believer': 'tt0247199',                    # Single-word genre
    'watchmen': 'tt0409459',                        # Runtimes: Director's Cut and Ultimate Cut
    'thale 2': 'tt2917940',                         # Unreleased movie

    # Title AKA regression tests
    'butterfly': 'tt0188030',
    'dead and buried': 'tt0082242',
    'hard boiled': 'tt0104684',
    'joy ride 3': 'tt3138376',
    'pusher 2': 'tt0396184',
    'sin nombre': 'tt1127715',
    'terror in the woods': 'tt7534328',
    'the human centipede 2': 'tt1530509',
}


@pytest.mark.parametrize(
    argnames='query, exp_query',
    argvalues=(
        (Query('Foo and Bar'), Query('foo bar')),
        (Query('Foo & Bar'), Query('foo & bar')),
        (Query('Cant See You'), Query("can't See You")),
        (Query('Wont See You'), Query("Won't See You")),
        (Query('Dont See You'), Query("Don't See You")),
        (Query('Want to See You'), Query("Want to See You")),
    ),
    ids=lambda value: str(value),
)
def test_sanitize_query(query, exp_query, api, store_response):
    return_value = api.sanitize_query(query)
    assert return_value == exp_query


@pytest.mark.parametrize(
    argnames='text, exp_id',
    argvalues=(
        ('Some Title', None),
        ('1984', None),
        ('tt0123arf', None),
        ('arftt0123', None),
        ('tt0123', 'tt0123'),
        ('https://www.imdb.com/title/tt0123/', 'tt0123'),
        ('https://www.imdb.com/title/tt0123', 'tt0123'),
        ('junk tt0123 more junk', 'tt0123'),
        ('junk https://www.imdb.com/title/tt0123/stuff more junk', 'tt0123'),
    ),
    ids=lambda value: str(value),
)
def test_get_id_from_text(text, exp_id, api, store_response):
    return_value = api.get_id_from_text(text)
    assert return_value == exp_id


@pytest.mark.parametrize(
    argnames='query, title, title_english, title_original, type, year, cast, countries, directors, genres, summary',
    argvalues=(
        (
            Query(id=ids['february']),
            "The Blackcoat's Daughter",
            "The Blackcoat's Daughter",
            'February',
            ReleaseType.movie,
            '2015',
            ('Emma Roberts', 'Kiernan Shipka', 'Lucy Boynton'),
            ('Canada', 'United States'),
            ('Oz Perkins',),
            ('horror', 'mystery', 'thriller'),
            ('Two girls must battle a mysterious evil force when they get left behind '
             'at their boarding school over winter break.'),
        ),
        (
            Query(id=ids['the bridge']),
            'The Bridge',
            'The Bridge',
            'Bron/Broen',
            ReleaseType.series,
            '2011',
            ('Sofia Helin', 'Rafael Pettersson', 'Sarah Boberg'),
            ('Sweden', 'Denmark', 'Germany', 'Norway'),
            (),
            ('crime', 'mystery', 'thriller'),
            ('When a body is found on the bridge between Denmark and Sweden, '
             'right on the border, Danish inspector Martin Rohde and Swedish '
             'Saga Norén have to share jurisdiction and work together to find the killer.'),
        ),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_handles_id_in_query(query, title, title_english, title_original, type, year,
                                          cast, countries, directors, genres, summary,
                                          api, store_response):
    results = await api.search(query)
    assert len(results) == 1
    assert results[0].id == query.id
    assert results[0].title == title
    assert results[0].type == type
    assert results[0].url == f'{imdb.ImdbApi._url_base}/title/{query.id}'
    assert results[0].year == year
    assert (await results[0].cast())[:3] == cast
    assert (await results[0].countries()) == countries
    assert (await results[0].directors()) == directors
    assert (await results[0].genres()) == genres
    assert (await results[0].summary()) == summary
    assert (await results[0].title_english()) == title_english
    assert (await results[0].title_original()) == title_original


@pytest.mark.asyncio
async def test_search_returns_empty_list_if_title_is_empty(api, store_response):
    assert await api.search(Query('', year='2009')) == []

@pytest.mark.asyncio
async def test_search_returns_list_of_SearchResults(api, store_response):
    results = await api.search(Query('blues brothers', type=ReleaseType.movie))
    for result in results:
        assert isinstance(result, SearchResult)


@pytest.mark.parametrize(
    argnames=('query', 'exp_ids'),
    argvalues=(
        (Query('blues brothers', year=1980), ('tt0080455',)),  # The Blues Brothers
        (Query('blues brothers', year='1998'), ('tt0118747',)),  # Blues Brothers 2000 (1998)
        (Query('blues brothers', year=1950), None),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_for_year(query, exp_ids, api, store_response):
    results = await api.search(query)
    ids = [r.id for r in results]
    if exp_ids:
        for exp_id in exp_ids:
            assert exp_id in ids
    else:
        assert not results


@pytest.mark.parametrize(
    argnames=('query', 'exp_ids'),
    argvalues=(
        (Query('blues brothers', type=ReleaseType.movie), ('tt0080455',)),   # 1980 movie
        (Query('blues brothers', type=ReleaseType.series), ('tt0472243',)),  # Animated series
        (Query('balada triste de trompeta', type=ReleaseType.series), None),
        (Query('time traveling bong', type=ReleaseType.movie), None),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_for_type(query, exp_ids, api, store_response):
    results = await api.search(query)
    ids = [r.id for r in results]
    if exp_ids:
        for exp_id in exp_ids:
            assert exp_id in ids
    else:
        assert not results


@pytest.mark.parametrize(
    argnames=('query', 'exp_cast'),
    argvalues=(
        (Query(id=ids['february']), ('Emma Roberts', 'Kiernan Shipka', 'Lucy Boynton')),
        (Query(id=ids['the bridge']), ('Sofia Helin', 'Rafael Pettersson', 'Sarah Boberg')),
        (Query(id=ids['the forest']), ('Samuel Labarthe', 'Suzanne Clément', 'Alexia Barlier')),
        (Query(id=ids['aftermath']), ()),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_cast(query, exp_cast, api, store_response):
    results = await api.search(query)
    cast = await results[0].cast()
    for member in exp_cast:
        assert member in cast


@pytest.mark.parametrize(
    argnames=('query', 'exp_countries'),
    argvalues=(
        (Query(id=ids['february']), ('Canada', 'United States')),
        (Query(id=ids['the bridge']), ('Sweden', 'Denmark', 'Germany', 'Norway')),
        (Query(id=ids['the forest']), ('France',)),
        (Query(id=ids['aftermath']), ('United Kingdom',)),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_country(query, exp_countries, api, store_response):
    results = await api.search(query)
    countries = await results[0].countries()
    assert countries == exp_countries


@pytest.mark.parametrize(
    argnames=('query', 'exp_id'),
    argvalues=(
        (Query(id=ids['february']), ids['february']),
        (Query(id=ids['the bridge']), ids['the bridge']),
        (Query(id=ids['the forest']), ids['the forest']),
        (Query(id=ids['aftermath']), ids['aftermath']),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_id(query, exp_id, api, store_response):
    results = await api.search(query)
    assert results[0].id == exp_id


@pytest.mark.parametrize(
    argnames=('query', 'exp_directors'),
    argvalues=(
        (Query(id=ids['february']), ('Oz Perkins',)),
        (Query(id=ids['the bridge']), ()),
        (Query(id=ids['the forest']), ()),
        (Query(id=ids['aftermath']), ('Nancy Diuguid',)),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_directors(query, exp_directors, api, store_response):
    results = await api.search(query)
    directors = await results[0].directors()
    assert directors == exp_directors


@pytest.mark.parametrize(
    argnames=('query', 'exp_genres'),
    argvalues=(
        (Query(id=ids['february']), ('horror', 'mystery', 'thriller')),
        (Query(id=ids['the bridge']), ('crime', 'mystery', 'thriller')),
        (Query(id=ids['the forest']), ('crime', 'drama')),
        (Query(id=ids['aftermath']), ('short', 'drama')),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_genres(query, exp_genres, api, store_response):
    results = await api.search(query)
    genres = await results[0].genres()
    assert genres == exp_genres


@pytest.mark.parametrize(
    argnames=('query', 'exp_summary'),
    argvalues=(
        (Query(id=ids['february']), ('Two girls must battle a mysterious evil force when they '
                                     'get left behind at their boarding school over winter break.')),
        (Query(id=ids['the bridge']), ('When a body is found on the bridge between Denmark and '
                                       'Sweden, right on the border, Danish inspector Martin Rohde '
                                       'and Swedish Saga Norén have to share jurisdiction and work '
                                       'together to find the killer.')),
        (Query(id=ids['the forest']), ('Sixteen-year-old Jennifer disappears one night from her '
                                       'village in the Ardennes. Captain Gaspard Deker leads the '
                                       'investigation with local cop Virginie Musso, who knew '
                                       'the girl well. They are helped by Eve, a lonely and mysterious woman.')),
        (Query(id=ids['wingwall auditions']), ''),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_summary(query, exp_summary, api, store_response):
    results = await api.search(query)
    summary = await results[0].summary()
    assert summary == exp_summary


@pytest.mark.parametrize(
    argnames='query, exp_title, exp_title_english, exp_title_original',
    argvalues=(
        (Query(id=ids['1899']), '1899', '', '1899'),
        (Query(id=ids['1984']), '1984', '', '1984'),
        (Query(id=ids['adu']), 'Adú', '', 'Adú'),
        (Query(id=ids['dead and buried']), 'Dead & Buried', '', 'Dead & Buried'),
        (Query(id=ids['february']), "The Blackcoat's Daughter", "The Blackcoat's Daughter", 'February'),
        (Query(id=ids['hard boiled']), 'Hard Boiled', 'Hard Boiled', 'Lat sau san taam'),
        (Query(id=ids['sin nombre']), 'Sin nombre', '', 'Sin nombre'),
        (Query(id=ids['the bridge']), 'The Bridge', 'The Bridge', 'Bron/Broen'),
        (Query(id=ids['the forest']), 'The Forest', 'The Forest', 'La forêt'),
        (Query(id=ids['aftermath']), 'Aftermath', '', 'Aftermath'),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_title_english_original(query, exp_title, exp_title_english, exp_title_original, api, store_response):
    results = await api.search(query)
    assert results[0].title == exp_title
    assert (await results[0].title_english()) == exp_title_english
    assert (await results[0].title_original()) == exp_title_original


@pytest.mark.parametrize(
    argnames=('query', 'exp_type'),
    argvalues=(
        (Query(id=ids['february']), ReleaseType.movie),
        (Query(id=ids['the bridge']), ReleaseType.season),
        (Query(id=ids['the forest']), ReleaseType.season),
        (Query(id=ids['aftermath']), ReleaseType.movie),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_type(query, exp_type, api, store_response):
    results = await api.search(query)
    assert results[0].type == exp_type


@pytest.mark.parametrize(
    argnames=('query', 'exp_url'),
    argvalues=(
        (Query(id=ids['february']), 'https://www.imdb.com/title/tt3286052'),
        (Query(id=ids['the bridge']), 'https://www.imdb.com/title/tt1733785'),
        (Query(id=ids['the forest']), 'https://www.imdb.com/title/tt6560040'),
        (Query(id=ids['aftermath']), 'https://www.imdb.com/title/tt0896516'),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_url(query, exp_url, api, store_response):
    results = await api.search(query)
    assert results[0].url == exp_url


@pytest.mark.parametrize(
    argnames=('query', 'exp_year'),
    argvalues=(
        (Query(id=ids['february']), '2015'),
        (Query(id=ids['the bridge']), '2011'),
        (Query(id=ids['the forest']), '2017'),
        (Query(id=ids['wingwall auditions']), ''),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_search_result_year(query, exp_year, api, store_response):
    results = await api.search(query)
    assert results[0].year == exp_year


@pytest.mark.asyncio
async def test_search_result_parser_failure(api):
    result = imdb._ImdbSearchResult(imdb_api=api)
    assert result.id == ''
    assert result.title == ''
    assert result.type == ReleaseType.movie
    assert result.url == ''
    assert result.year == ''
    assert await result.cast() == ()
    assert await result.countries() == ()
    assert await result.directors() == ()
    assert await result.genres() == ()
    assert await result.summary() == ''
    assert await result.title_english() == ''
    assert await result.title_original() == ''


@pytest.mark.parametrize(
    argnames=('id', 'exp_cast'),
    argvalues=(
        (ids['pygmalion'], (("Peter O'Toole", 'https://www.imdb.com/name/nm0000564'),
                            ('Shelagh McLeod', 'https://www.imdb.com/name/nm0572870'),
                            ('Nancy Kerr', 'https://www.imdb.com/name/nm0449770'))),
        (ids['wind in the willows'], (('Alan Bennett', 'https://www.imdb.com/name/nm0003141'),
                                      ('Michael Palin', 'https://www.imdb.com/name/nm0001589'),
                                      ('Michael Gambon', 'https://www.imdb.com/name/nm0002091'))),
        (ids['benders big score'], (('Billy West', 'https://www.imdb.com/name/nm0921942'),
                                    ('Katey Sagal', 'https://www.imdb.com/name/nm0005408'),
                                    ('John DiMaggio', 'https://www.imdb.com/name/nm0224007'))),
        (ids['elephant'], (('Gary Walker', 'https://www.imdb.com/name/nm1281884'),
                           ('Bill Hamilton', 'https://www.imdb.com/name/nm1685093'),
                           ('Michael Foyle', 'https://www.imdb.com/name/nm0289432'))),
        (ids['kung fury'], (('David Sandberg', 'https://www.imdb.com/name/nm6247887'),
                            ('Jorma Taccone', 'https://www.imdb.com/name/nm1672246'),
                            ('Steven Chew', 'https://www.imdb.com/name/nm7320022'))),
        (ids['the forest'], (('Samuel Labarthe', 'https://www.imdb.com/name/nm0479355'),
                             ('Suzanne Clément', 'https://www.imdb.com/name/nm0167501'),
                             ('Alexia Barlier', 'https://www.imdb.com/name/nm1715145'))),
        (ids['the bridge'], (('Sofia Helin', 'https://www.imdb.com/name/nm0375138'),
                             ('Rafael Pettersson', 'https://www.imdb.com/name/nm1142392'),
                             ('Sarah Boberg', 'https://www.imdb.com/name/nm0090360'))),
        (ids['the bridge s02e03'], (('Sofia Helin', 'https://www.imdb.com/name/nm0375138'),
                                    ('Kim Bodnia', 'https://www.imdb.com/name/nm0091035'),
                                    ('Dag Malmberg', 'https://www.imdb.com/name/nm0540216'))),
        (ids['aftermath'], ()),
        (None, ()),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_cast(id, exp_cast, api, store_response):
    cast = (await api.cast(id))[:3]
    if not cast:
        assert exp_cast == ()
    else:
        for person, (name, url) in zip_longest(cast, exp_cast):
            assert person == name
            assert person.url == url


@pytest.mark.parametrize(
    argnames=('id', 'exp_countries'),
    argvalues=(
        (ids['february'], ('Canada', 'United States')),  # Movie
        (ids['wind in the willows'], ('United Kingdom',)),  # TV Movie
        (ids['benders big score'], ('United States',)),  # Video
        (ids['elephant'], ('United Kingdom',)),  # TV movie
        (ids['kung fury'], ('Sweden',)),  # Short
        (ids['the bridge'], ('Sweden', 'Denmark', 'Germany', 'Norway')),  # Series
        (ids['the bridge s02e03'], ()),  # Episode
        (None, ()),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_countries(id, exp_countries, api, store_response):
    countries = await api.countries(id)
    assert countries == exp_countries


@pytest.mark.parametrize(
    argnames=('id', 'exp_creators'),
    argvalues=(
        (ids['february'], (('Oz Perkins', 'https://www.imdb.com/name/nm0674020'),)),  # Movie
        (ids['wind in the willows'], (('Kenneth Grahame', 'https://www.imdb.com/name/nm0334370'),  # TV Movie
                                      ('Ted Walker', 'https://www.imdb.com/name/nm0908249'))),
        (ids['benders big score'], (('Matt Groening', 'https://www.imdb.com/name/nm0004981'),  # Video
                                    ('David X. Cohen', 'https://www.imdb.com/name/nm0169326'),
                                    ('Ken Keeler', 'https://www.imdb.com/name/nm0444517'))),
        (ids['elephant'], (('Bernard MacLaverty', 'https://www.imdb.com/name/nm0533735'),)),  # TV Movie
        (ids['kung fury'], (('David Sandberg', 'https://www.imdb.com/name/nm6247887'),)),  # Short
        (ids['the forest'], (('Delinda Jacobs', 'https://www.imdb.com/name/nm3064398'),)),  # Miniseries
        (ids['the bridge'], (('Måns Mårlind', 'https://www.imdb.com/name/nm0617523'),
                             ('Hans Rosenfeldt', 'https://www.imdb.com/name/nm0742577'),
                             ('Björn Stein', 'https://www.imdb.com/name/nm0825407'))),  # Series
        (ids['the bridge s02e03'], (('Hans Rosenfeldt', 'https://www.imdb.com/name/nm0742577'),  # Episode
                                    ('Måns Mårlind', 'https://www.imdb.com/name/nm0617523'),
                                    ('Björn Stein', 'https://www.imdb.com/name/nm0825407'))),
        (None, ()),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_creators(id, exp_creators, api, store_response):
    creators = await api.creators(id)
    if not creators:
        assert exp_creators == ()
    else:
        for person, (name, url) in zip_longest(creators, exp_creators, fillvalue=(None, None)):
            assert person == name
            assert person.url == url


@pytest.mark.parametrize(
    argnames=('id', 'exp_directors'),
    argvalues=(
        (ids['february'], (('Oz Perkins', 'https://www.imdb.com/name/nm0674020'),)),  # Movie
        (ids['wind in the willows'], (('Dave Unwin', 'https://www.imdb.com/name/nm0881386'),  # TV Movie
                                      ('Dennis Abey', 'https://www.imdb.com/name/nm0008688'))),
        (ids['benders big score'], (('Dwayne Carey-Hill', 'https://www.imdb.com/name/nm1401752'),)),  # Video
        (ids['elephant'], (('Alan Clarke', 'https://www.imdb.com/name/nm0164639'),)),  # TV movie
        (ids['kung fury'], (('David Sandberg', 'https://www.imdb.com/name/nm6247887'),)),  # Short
        (ids['the forest'], ()),  # Miniseries
        (ids['the bridge'], ()),  # Series
        (ids['the bridge s02e03'], (('Henrik Georgsson', 'https://www.imdb.com/name/nm1380082'),)),  # Episode
        (None, ()),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_directors(id, exp_directors, api, store_response):
    directors = await api.directors(id)
    if not directors:
        assert exp_directors == ()
    else:
        for person, (name, url) in zip_longest(directors[:3], exp_directors, fillvalue=(None, None)):
            assert person == name
            assert person.url == url


@pytest.mark.parametrize(
    argnames=('id', 'exp_genres'),
    argvalues=(
        (ids['the believer'], ('drama',)),
        (ids['february'], ('horror', 'mystery', 'thriller')),
        (ids['wind in the willows'], ('animation', 'family')),
        (ids['benders big score'], ('animation', 'comedy', 'musical')),
        (ids['elephant'], ('crime', 'drama')),
        (ids['kung fury'], ('short', 'action', 'comedy')),
        (ids['the forest'], ('crime', 'drama')),
        (ids['the bridge'], ('crime', 'mystery', 'thriller')),
        (ids['the bridge s02e03'], ('crime', 'mystery', 'thriller')),
        (None, ()),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_genres(id, exp_genres, api, store_response):
    genres = await api.genres(id)
    assert genres == exp_genres


@pytest.mark.parametrize(
    argnames='id, exp_poster_url',
    argvalues=(
        # Movie
        (ids['february'], 'https://m.media-amazon.com/images/M/MV5BMTY2NTQ3NTEzNF5BMl5BanBnXkFtZTgwMzA0MzY1OTE@._V1_.jpg'),
        # TV movie
        (ids['wind in the willows'], 'https://m.media-amazon.com/images/M/MV5BOGQ3NWM5OTAtOThjZS00MzMyLTkwZjMtOWIyOTdlZjFiZGI1XkEyXkFqcGdeQXVyNzMwOTY2NTI@._V1_.jpg'),
        # Video
        (ids['benders big score'], 'https://m.media-amazon.com/images/M/MV5BM2U3NmRiNDItMDQwYy00Y2Q0LWJiYzItNjAzNThkZjFlM2RiXkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_.jpg'),
        # TV movie
        (ids['elephant'], 'https://m.media-amazon.com/images/M/MV5BMWE0ZTBiOWItY2ZkNS00MzI0LWE5Y2QtYjJmNjM1MGRkZGNmXkEyXkFqcGdeQXVyMzU0MTk1Nzc@._V1_.jpg'),
        # Short
        (ids['kung fury'], 'https://m.media-amazon.com/images/M/MV5BMjQwMjU2ODU5NF5BMl5BanBnXkFtZTgwNTU1NjM4NTE@._V1_.jpg'),
        # Miniseries
        (ids['the forest'], 'https://m.media-amazon.com/images/M/MV5BMzY5NThkOWItN2I1OC00MzQ2LThlYjktMGExYTk2YzM1ZGRmXkEyXkFqcGdeQXVyODEyMzI2OTE@._V1_.jpg'),
        # Series
        (ids['the bridge'], 'https://m.media-amazon.com/images/M/MV5BMjQ3MDAzNDU4NV5BMl5BanBnXkFtZTgwNjE2NDQ0NzE@._V1_.jpg'),
        # Episode
        (ids['the bridge s02e03'], 'https://m.media-amazon.com/images/M/MV5BZDc0NDY1ZDUtN2MyMy00YTg3LWJkZTktNThhYmRiYTlkOTM0L2ltYWdlXkEyXkFqcGdeQXVyNjg2MjkwNTQ@._V1_.jpg'),
        # No poster
        (ids['wingwall auditions'], ''),
        (None, ''),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_poster_url(id, exp_poster_url, api, store_response):
    poster_url = await api.poster_url(id)
    assert poster_url == exp_poster_url


@pytest.mark.parametrize(
    argnames=('id', 'exp_rating'),
    argvalues=(
        (ids['february'], 5.9),  # Movie
        (ids['wind in the willows'], 7.4),  # TV movie
        (ids['benders big score'], 7.6),  # Video
        (ids['elephant'], 7.1),  # TV movie
        (ids['kung fury'], 8.0),  # Short
        (ids['the forest'], 7.2),  # Miniseries
        (ids['the bridge'], 8.6),  # Series
        (ids['the bridge s02e03'], 8.0),  # Episode
        (None, None),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_rating(id, exp_rating, api, store_response):
    rating = await api.rating(id)
    assert rating == exp_rating


@pytest.mark.parametrize(
    argnames=('id', 'exp_runtimes'),
    argvalues=(
        (ids['watchmen'], {'default': 162, "Director's Cut": 186, 'Ultimate Cut': 215}),  # Movie
        (ids['wind in the willows'], {'default': 73}),  # TV movie
        (ids['benders big score'], {'default': 88}),  # Video
        (ids['elephant'], {'default': 39}),  # TV movie
        (ids['kung fury'], {'default': 31}),  # Short
        (ids['the forest'], {'Entire Series': 313}),  # Miniseries
        (ids['the bridge'], {'default': 60}),  # Series
        (ids['the bridge s02e03'], {'default': 57}),  # Episode
        (ids['wingwall auditions'], {}),  # No runtime found
        (None, {}),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_runtimes(id, exp_runtimes, api, store_response):
    runtimes = await api.runtimes(id)
    assert runtimes == exp_runtimes


@pytest.mark.parametrize(
    argnames=('id', 'exp_summary'),
    argvalues=(
        (ids['february'], ('Two girls must battle a mysterious evil force when they get left '
                           'behind at their boarding school over winter break.')),  # Movie
        (ids['wind in the willows'], ('When three close friends Mole, Ratty and Badger '
                                      'find out that the infamous Mr. Toad of Toad Hall '
                                      'has been up to no good, they must find him and change '
                                      'his ways for good.')),  # TV movie
        (ids['benders big score'], ('Planet Express sees a hostile takeover and Bender falls into the hands of '
                                    'criminals where he is used to fulfill their schemes.')),  # Video
        (ids['elephant'], ('A depiction of a series of violent killings in Northern Ireland '
                           'with no clue as to exactly who is responsible.')),  # TV Short
        (ids['kung fury'], ('In 1985, Kung Fury, the toughest martial artist cop in Miami, '
                            'goes back in time to kill the worst criminal of all time '
                            '- Kung Führer, a.k.a. Adolf Hitler.')),  # Short
        (ids['the forest'], ('Sixteen-year-old Jennifer disappears one night from her village '
                             'in the Ardennes. Captain Gaspard Deker leads the investigation with '
                             'local cop Virginie Musso, who knew the girl well. They are helped '
                             'by Eve, a lonely and mysterious woman.')),  # Miniseries
        (ids['the bridge'], ('When a body is found on the bridge between Denmark and Sweden, '
                             'right on the border, Danish inspector Martin Rohde and Swedish '
                             'Saga Norén have to share jurisdiction and work together to find the killer.')),  # Series
        (ids['the bridge s02e03'], ('Saga and Martin continue their hunt for the eco-terrorists, '
                                    'who have realised the police are on their trail.')),  # Episode
        (ids['wingwall auditions'], ''),  # No summary found
        (None, ''),
    ),
    ids=lambda value: str(value)[:30] or '<empty>',
)
@pytest.mark.asyncio
async def test_summary(id, exp_summary, api, store_response):
    summary = await api.summary(id)
    if isinstance(exp_summary, str):
        assert summary == exp_summary
    else:
        assert any(summary == exp_sum for exp_sum in exp_summary)


@pytest.mark.parametrize(
    argnames=('id', 'exp_title_english', 'exp_title_original'),
    argvalues=(
        (ids['1984'], '', '1984'),
        (ids['dead and buried'], '', 'Dead & Buried'),
        (ids['hard boiled'], 'Hard Boiled', 'Lat sau san taam'),
        (ids['butterfly'], 'Butterfly', 'La lengua de las mariposas'),
        (ids['the nest'], 'The Nest', 'Nid de guêpes'),
        (ids['pusher 2'], '', 'Pusher II'),
        (ids['sin nombre'], '', 'Sin nombre'),
        (ids['ao'], '', 'Ao, le dernier Néandertal'),
        (ids['the human centipede 2'], '', 'The Human Centipede II (Full Sequence)'),
        (ids['3 days to kill'], '', '3 Days to Kill'),
        (ids['joy ride 3'], '', 'Joy Ride 3: Road Kill'),
        (ids['february'], "The Blackcoat's Daughter", 'February'),
        (ids['the forest'], 'The Forest', 'La forêt'),
        (ids['terror in the woods'], '', 'Terror in the Woods'),
        (ids['1899'], '', '1899'),
        (ids['adu'], '', 'Adú'),
        (None, '', ''),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_title_english_original(id, exp_title_english, exp_title_original, api, store_response):
    title_original = await api.title_original(id)
    title_english = await api.title_english(id)
    print('original:', title_original, '-- expected:', exp_title_original)
    print('english:', title_english, '-- expected:', exp_title_english)
    assert title_original == exp_title_original
    assert title_english == exp_title_english
    assert await api.title_english(id, default_to_original=False) == exp_title_english
    if exp_title_english:
        assert await api.title_english(id, default_to_original=True) == exp_title_english
    else:
        assert await api.title_english(id, default_to_original=True) == exp_title_original


@pytest.mark.parametrize(
    argnames=('id', 'exp_type'),
    argvalues=(
        (ids['february'], ReleaseType.movie),  # Movie
        (ids['wind in the willows'], ReleaseType.movie),  # TV movie
        (ids['benders big score'], ReleaseType.movie),  # Video
        (ids['elephant'], ReleaseType.movie),  # TV movie
        (ids['kung fury'], ReleaseType.movie),  # Short
        (ids['the forest'], ReleaseType.season),  # Miniseries
        (ids['the bridge'], ReleaseType.season),  # Series
        (ids['the bridge s02e03'], ReleaseType.episode),  # Episode
        (None, ReleaseType.unknown),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_type(id, exp_type, api, store_response):
    assert await api.type(id) is exp_type


@pytest.mark.asyncio
async def test_url(api):
    assert await api.url('foo') == api._url_base + '/title/foo'
    assert await api.url(None) == ''


@pytest.mark.parametrize(
    argnames=('id', 'exp_year'),
    argvalues=(
        (ids['1984'], '1956'),  # Movie with digit-only title
        (ids['1899'], '2022'),  # Series with digit-only title
        (ids['february'], '2015'),  # Movie
        (ids['wind in the willows'], '1995'),  # TV movie
        (ids['benders big score'], '2007'),  # Video
        (ids['elephant'], '1989'),  # TV movie
        (ids['kung fury'], '2015'),  # Short
        (ids['the forest'], '2017'),  # Miniseries
        (ids['the bridge'], '2011'),  # Series
        (ids['the bridge s02e03'], '2013'),  # Episode
        (ids['thale 2'], ''),  # Unreleased movie
        (None, ''),
    ),
    ids=lambda value: str(value),
)
@pytest.mark.asyncio
async def test_year(id, exp_year, api, store_response):
    assert await api.year(id) == exp_year

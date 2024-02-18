from mfire.utils.geo import CompassRose8, CompassRose16, distance_on_earth


def test_from_azimut():
    assert CompassRose8.from_azimut(60) == CompassRose8.NE
    assert CompassRose16.from_azimut(60) == CompassRose16.ENE
    assert CompassRose8.from_azimut(359) == CompassRose8.N
    assert CompassRose16.from_azimut(359) == CompassRose16.N
    assert CompassRose8.from_azimut(540) == CompassRose8.S


def test_opposite():
    assert CompassRose8.N.opposite == CompassRose8.S
    assert CompassRose16.N.opposite == CompassRose16.S

    assert all(d.opposite == d + 180 for d in CompassRose8)
    assert all(d.opposite == d + 180 for d in CompassRose16)


def test_text_descriptions():
    assert CompassRose8.N.description == "Nord"
    assert CompassRose8.N.text == "le Nord"
    assert CompassRose8.N.short_description == "Nord"

    assert CompassRose16.ENE.description == "Est-Nord-Est"
    assert CompassRose16.ENE.text == "l'Est-Nord-Est"
    assert CompassRose16.ENE.short_description == "ENE"


def test_azimut():
    assert round(CompassRose8.azimut((0, 0), (1, 1)), 2) == 45


def test_from_points():
    assert CompassRose8.from_points((0, 0), (1, 1)) == CompassRose8.NE
    assert CompassRose16.from_points((0, 0), (1, 2)) == CompassRose16.NNE
    assert CompassRose8.from_points((0, 0), (1, 2)) == CompassRose8.NE


def test_distance_on_earth():
    assert round(distance_on_earth((1.370, 43.563), (35.800, 34.164)), 2) == 3136.01

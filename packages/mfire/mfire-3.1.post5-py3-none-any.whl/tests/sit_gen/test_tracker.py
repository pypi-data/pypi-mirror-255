from mfire.sit_gen.tracker import Tracker

OBJECTS = {
    "2022-06-08T00:00:00.000000000": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "front froid",
                    "validity_time": "2022-06-08T00:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[[-18, 50], [-16, 51]], [[-16, 51], [-14, 53]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "front froid",
                    "validity_time": "2022-06-08T00:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[[-23, 39], [-21, 40]], [[-21, 40], [-19, 42]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "depression",
                    "validity_time": "2022-06-08T00:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {"type": "Point", "coordinates": [-15, 52]},
            },
        ],
    },
    "2022-06-08T03:00:00.000000000": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "front froid",
                    "validity_time": "2022-06-08T03:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[[-17, 50], [-15, 51]], [[-15, 51], [-13, 53]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "front froid",
                    "validity_time": "2022-06-08T03:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[[-23, 38], [-21, 39]], [[-21, 39], [-19, 41]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "depression",
                    "validity_time": "2022-06-08T03:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {"type": "Point", "coordinates": [-14, 52]},
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "anticyclone",
                    "validity_time": "2022-06-08T03:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {"type": "Point", "coordinates": [0, 31]},
            },
        ],
    },
    "2022-06-08T06:00:00.000000000": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "front froid",
                    "validity_time": "2022-06-08T06:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[[-16, 50], [-14, 51]], [[-14, 51], [-13, 53]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "front froid",
                    "validity_time": "2022-06-08T06:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[[-23, 38], [-21, 38.5]], [[-21, 38.5], [-19, 40]]],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "depression",
                    "validity_time": "2022-06-08T06:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {"type": "Point", "coordinates": [-13, 52]},
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "anticyclone",
                    "validity_time": "2022-06-08T06:00:00.000000000",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                },
                "geometry": {"type": "Point", "coordinates": [1, 32]},
            },
        ],
    },
}

RESULT = {
    "anticyclones": [
        [
            {
                "geometry": {"coordinates": [0, 31], "type": "Point"},
                "properties": {
                    "direction": "le Nord-Est",
                    "name": "anticyclone",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                    "validity_time": "2022-06-08T03:00:00.000000000",
                },
                "type": "Feature",
            },
            {
                "geometry": {"coordinates": [1, 32], "type": "Point"},
                "properties": {
                    "direction": "le Nord-Est",
                    "name": "anticyclone",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                    "validity_time": "2022-06-08T06:00:00.000000000",
                },
                "type": "Feature",
            },
        ]
    ],
    "joined_depressions_fronts": [
        (
            [
                {
                    "geometry": {"coordinates": [-15, 52], "type": "Point"},
                    "properties": {
                        "direction": "l'Est",
                        "name": "depression",
                        "reference_time": "2022-06-08T00:00:00.000000000",
                        "validity_time": "2022-06-08T00:00:00.000000000",
                    },
                    "type": "Feature",
                },
                {
                    "geometry": {"coordinates": [-14, 52], "type": "Point"},
                    "properties": {
                        "direction": "l'Est",
                        "name": "depression",
                        "reference_time": "2022-06-08T00:00:00.000000000",
                        "validity_time": "2022-06-08T03:00:00.000000000",
                    },
                    "type": "Feature",
                },
                {
                    "geometry": {"coordinates": [-13, 52], "type": "Point"},
                    "properties": {
                        "direction": "l'Est",
                        "name": "depression",
                        "reference_time": "2022-06-08T00:00:00.000000000",
                        "validity_time": "2022-06-08T06:00:00.000000000",
                    },
                    "type": "Feature",
                },
            ],
            [
                {
                    "geometry": {
                        "coordinates": [[[-18, 50], [-16, 51]], [[-16, 51], [-14, 53]]],
                        "type": "MultiLineString",
                    },
                    "properties": {
                        "direction": "l'Est",
                        "name": "front froid",
                        "reference_time": "2022-06-08T00:00:00.000000000",
                        "validity_time": "2022-06-08T00:00:00.000000000",
                    },
                    "type": "Feature",
                },
                {
                    "geometry": {
                        "coordinates": [[[-17, 50], [-15, 51]], [[-15, 51], [-13, 53]]],
                        "type": "MultiLineString",
                    },
                    "properties": {
                        "direction": "l'Est",
                        "name": "front froid",
                        "reference_time": "2022-06-08T00:00:00.000000000",
                        "validity_time": "2022-06-08T03:00:00.000000000",
                    },
                    "type": "Feature",
                },
                {
                    "geometry": {
                        "coordinates": [[[-16, 50], [-14, 51]], [[-14, 51], [-13, 53]]],
                        "type": "MultiLineString",
                    },
                    "properties": {
                        "direction": "l'Est",
                        "name": "front froid",
                        "reference_time": "2022-06-08T00:00:00.000000000",
                        "validity_time": "2022-06-08T06:00:00.000000000",
                    },
                    "type": "Feature",
                },
            ],
        )
    ],
    "depressions": [],
    "fronts": [
        [
            {
                "geometry": {
                    "coordinates": [[[-23, 39], [-21, 40]], [[-21, 40], [-19, 42]]],
                    "type": "MultiLineString",
                },
                "properties": {
                    "direction": "le Sud",
                    "name": "front froid",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                    "validity_time": "2022-06-08T00:00:00.000000000",
                },
                "type": "Feature",
            },
            {
                "geometry": {
                    "coordinates": [[[-23, 38], [-21, 39]], [[-21, 39], [-19, 41]]],
                    "type": "MultiLineString",
                },
                "properties": {
                    "direction": "le Sud",
                    "name": "front froid",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                    "validity_time": "2022-06-08T03:00:00.000000000",
                },
                "type": "Feature",
            },
            {
                "geometry": {
                    "coordinates": [[[-23, 38], [-21, 38.5]], [[-21, 38.5], [-19, 40]]],
                    "type": "MultiLineString",
                },
                "properties": {
                    "direction": "le Sud",
                    "name": "front froid",
                    "reference_time": "2022-06-08T00:00:00.000000000",
                    "validity_time": "2022-06-08T06:00:00.000000000",
                },
                "type": "Feature",
            },
        ]
    ],
}


def test_tracker():
    assert Tracker().run(OBJECTS) == RESULT

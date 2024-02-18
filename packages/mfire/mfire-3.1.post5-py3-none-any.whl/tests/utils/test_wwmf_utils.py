from itertools import product
from random import choice, sample
from typing import List

import pytest

from mfire.utils.wwmf_utils import (
    WWMF_FAMILIES,
    WWMF_SUBGRP,
    are_wwmf_precipitations,
    are_wwmf_visibilities,
    is_wwmf_rain,
    is_wwmf_severe,
    is_wwmf_shower,
    is_wwmf_snow,
    is_wwmf_thunderstorm,
    wwmf_families,
    wwmf_label,
)


def _sample_datasets(*args, label: str) -> List:
    """
    Return a list of possible TS datasets.

    Args:
        *args: Variable number of arguments representing the datasets.
        label (str): The label for the datasets.

    Returns:
        List: List of possible TS datasets.
    """

    def _sample(r):
        # Generate indices that satisfy the sum and maximum value conditions
        indices = [
            c
            for c in product(range(1, r), repeat=len(args))
            if sum(c) == r and all(c[i] <= len(arg.value) for i, arg in enumerate(args))
        ]

        result = []
        for indice in indices:
            # Generate combinations of datasets based on the indices
            result += [
                (
                    sum(
                        (sample(arg.value, indice[i]) for i, arg in enumerate(args)),
                        start=[],
                    ),
                    label,
                )
            ]
        return result

    r_max = sum(len(arg.value) for arg in args)
    return sum(
        (_sample(r) for r in range(3, r_max + 1)),
        start=[],
    )


dataset_wwmf_label = [
    # 1TS
    ([30], "Brume/brouillard"),
    ([31], "Brume"),
    ([32], "Brouillard"),
    ([33], "Brouillard dense"),
    ([38], "Brouillard givrant"),
    ([39], "Brouillard dense givrant"),
    ([40], "Bruine"),
    ([49], "Bruine verglaçante"),
    ([50], "Pluie"),
    ([51], "Pluie faible"),
    ([52], "Pluie modérée"),
    ([53], "Pluie forte"),
    ([58], "Pluie et neige mêlées"),
    ([59], "Pluie verglaçante"),
    ([60], "Neige"),
    ([61], "Neige faible"),
    ([62], "Neige modérée"),
    ([63], "Neige forte"),
    ([70], "Averses"),
    ([71], "Rares averses"),
    # ([72], "Rares averses avec ciel ouvert"),
    # ([73], "Averses avec ciel couvert"),
    ([77], "Averses de pluie et neige mêlées"),
    # ([78], "Averses de pluie et neige mêlées avec ciel couvert"),
    ([80], "Averses de neige"),
    ([81], "Rares averses de neige"),
    # (
    #     [
    #         82
    #     ],
    #     "Rares averses de neige avec ciel couvert"
    # ),
    # (
    #     [
    #         83
    #     ],
    #     "Averses de neige avec ciel couvert"
    # ),
    ([84], "Averses de grésil"),
    ([85], "Averses de grêle"),
    ([90], "Orages"),
    ([91], "Orages possibles"),
    ([92], "Averses orageuses"),
    ([93], "Orages avec pluie"),
    ([97], "Orages avec neige"),
    ([98], "Orages avec grêle"),
    ([99], "Orages violents"),
    # 2TS Visibility family
    ([32, 33], "Brouillard, parfois dense"),
    ([32, 38], "Brouillard, parfois givrant"),
    ([32, 39], "Brouillard, parfois dense et givrant"),
    ([33, 38], "Brouillard dense ou givrant"),
    ([33, 39], "Brouillard dense, parfois givrant"),
    ([38, 39], "Brouillard givrant, parfois dense"),
    ([30, 32], "Brouillard"),
    ([30, 33], "Brouillard, parfois dense"),
    ([30, 38], "Brouillard parfois givrant"),
    ([30, 39], "Brouillard, parfois dense et givrant"),
    # 2TS Family precipitation > Subfamily rain
    ([40, 49], "Bruine, parfois verglaçante"),
    ([49, choice([51, 52, 53])], "Bruine verglaçante ou pluie"),
    ([49, 59], "Précipitations verglaçantes"),
    ([51, 52], "Pluie faible à modérée"),
    ([51, 53], "Pluie"),
    ([52, 53], "Pluie modérée à forte"),
    ([choice([51, 52, 53]), 58], "Pluie, parfois mêlée de neige"),
    ([choice([51, 52, 53]), 59], "Pluie, parfois verglaçante"),
    # 2TS Family precipitation > Subfamily snow
    ([58, choice([61, 62, 63])], "Neige prédominante"),
    ([61, 62], "Neige parfois modérée"),
    ([61, 63], "Neige parfois forte"),
    ([62, 63], "Neige parfois forte"),
    (
        [choice([61, 62, 63]), choice([80, 81, 82, 83])],
        "Épisodes neigeux",
    ),
    # 2TS Family precipitation > Subfamily shower
    ([70, choice([71, 72, 73])], "Averses"),
    ([71, 72], "Rares averses"),
    ([71, 73], "Averses"),
    # ([72, 73], "Averses avec ciel couvert"),
    (
        [choice([70, 71, 72, 73]), choice([77, 78])],
        "Averses, parfois mêlées de neige",
    ),
    # ([77, 78], "Averses mêlées de neige"),
    ([80, choice([81, 82, 83])], "Averses de neige"),
    ([82, 83], "Averses de neige"),
    ([70, choice([80, 81, 82, 83])], "Averses, parfois neigeuses"),
    ([71, choice([80, 83])], "Averses, parfois neigeuses"),
    ([choice([71, 72]), choice([81, 82])], "Rares averses, parfois neigeuses"),
    ([73, choice([80, 81])], "Averses, parfois neigeuses"),
    # ([73, choice([82, 83])], "Averses avec ciel couvert, parfois neigeuses"),
    ([84, 85], "Averses de grésil ou grêle"),
    ([choice([70, 71, 72, 73]), 92], "Averses, parfois orageuses"),
    # 2TS Family precipitation > Subfamily thunderstorm
    ([84, 92], "Averses de grésil parfois orageuses"),
    ([85, 92], "Averses orageuses parfois avec grêle"),
    ([85, 98], "Orages ou averses avec grêle"),
    ([91, 92], "Orages et averses orageuses"),
    ([91, 93], "Orages parfois avec pluie"),
    ([91, 97], "Orages, parfois avec neige"),
    ([93, 98], "Orages avec pluie et grêle"),
    ([93, 99], "Orages parfois violents avec pluie"),
    ([97, 99], "Orages, parfois violents avec neige"),
    ([98, 99], "Orages violents avec grêle"),
    # 2TS Family precipitation > several subfamilies
    ([51, 61], "Précipitations faibles, parfois neigeuses"),
    ([52, 62], "Précipitations modérées, parfois neigeuses"),
    ([53, 63], "Précipitations fortes, parfois neigeuses"),
    ([choice([51, 52, 53]), choice([80, 81, 82, 83])], "Pluie, averses de neige"),
    ([choice([51, 52, 53]), choice([91, 93])], "Pluie ou orages"),
    ([choice([51, 52, 53]), 98], "Pluie ou orages avec grêle"),
    ([choice([51, 52, 53]), 99], "Pluie ou orages violents"),
    ([choice([61, 62, 63]), choice([70, 71, 72, 73])], "Averses, neige"),
    ([choice([61, 62, 63]), choice([91, 97])], "Orages, neige"),
    ([choice([61, 62, 63]), 98], "Giboulées orageuses, neige"),
    ([choice([61, 62, 63]), 99], "Orages violents, neige"),
    ([choice([70, 71, 72, 73]), choice([91, 93])], "Averses ou orages"),
    ([choice([70, 71, 72, 73]), 98], "Averses ou orages avec grêle"),
    ([choice([70, 71, 72, 73]), 99], "Averses ou orages violents"),
    ([choice([80, 81, 82, 83]), choice([91, 97])], "Orages, averses de neige"),
    ([choice([80, 81, 82, 83]), 98], "Giboulées orageuses, neige"),
    ([choice([80, 81, 82, 83]), 99], "Orages violents, neige"),
    # >= 3TS family visibility
    ([31, 32, 33], "Temps brumeux avec brouillard, parfois dense"),
    ([31, 32, 38], "Temps brumeux avec brouillard, parfois givrant"),
    ([31, 32, 39], "Temps brumeux avec brouillard, parfois dense et givrant"),
    ([32, 33, 38], "Brouillard, parfois dense ou givrant"),
    ([32, 33, 39], "Brouillard, parfois dense et givrant"),
    ([32, 38, 39], "Brouillard, parfois givrant et dense"),
    ([33, 38, 39], "Brouillard dense ou givrant"),
    ((30, 32, 33), "Brouillard, parfois dense"),
    ((30, 32, 38), "Brouillard, parfois givrant"),
    ((30, 32, 39), "Brouillard, parfois dense et givrant"),
    ((30, 33, 38), "Brouillard dense ou givrant"),
    ((30, 33, 39), "Brouillard dense, parfois givrant"),
    ((30, 38, 39), "Brouillard givrant, parfois dense"),
    (
        [31, 32, 33, choice([38, 39])],
        "Temps brumeux avec brouillard, parfois dense ou givrant",
    ),
    ([31, 33, 38, 39], "Temps brumeux avec brouillard, parfois dense et givrant"),
    ([32, 33, 38, 39], "Brouillard, parfois dense ou givrant"),
    ([30, 32, 33, 38], "Brouillard, parfois dense ou givrant"),
    ([30, 32, 33, 39], "Brouillard, parfois dense et givrant"),
    ([30, 32, 38, 39], "Brouillard, parfois givrant et dense"),
    ([30, 33, 38, 39], "Brouillard dense ou givrant"),
    ([31, 32, 33, 38, 39], "Temps brumeux avec brouillard, parfois dense ou givrant"),
    ([30, 32, 33, 38, 39], "Brouillard, parfois dense ou givrant"),
    # >=3 TS family precipitation with 1 or 2 subgroups
    *_sample_datasets(WWMF_SUBGRP.A1, label="Pluie"),
    *_sample_datasets(WWMF_SUBGRP.A2, label="Neige"),
    # *_sample_datasets(WWMF_SUBGRP.A3, label="Averses", r_min=3),
    # *_sample_datasets(WWMF_SUBGRP.A4, label="Averses de neige", r_min=3),
    *_sample_datasets(WWMF_SUBGRP.A5, label="Temps orageux"),
    *_sample_datasets(WWMF_SUBGRP.A1, WWMF_SUBGRP.A2, label="Pluie, neige"),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A1, WWMF_SUBGRP.A3, label="Pluie ou averses", r_min=3
    # ),
    # *_sample_datasets(WWMF_SUBGRP.A1, WWMF_SUBGRP.A4, label="Pluie, averses de "
    # "neige", r_min=3),
    *_sample_datasets(WWMF_SUBGRP.A1, WWMF_SUBGRP.A5, label="Pluie ou orages"),
    *_sample_datasets(
        WWMF_SUBGRP.A1, WWMF_SUBGRP.B1, label="Pluie parfois verglaçante"
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1, WWMF_SUBGRP.B2, label="Pluie ou averses de grésil"
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1, WWMF_SUBGRP.B3, label="Pluie ou averses de grêle"
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1, WWMF_SUBGRP.B4, label="Pluie ou orages avec grêle"
    ),
    *_sample_datasets(WWMF_SUBGRP.A1, WWMF_SUBGRP.B5, label="Pluie ou orages violents"),
    # *_sample_datasets(WWMF_SUBGRP.A2, WWMF_SUBGRP.A3, label="Averses, neige",
    # r_min=3),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A2,
    #     WWMF_SUBGRP.A4,
    #     label="Épisodes neigeux",
    #     r_min=3,
    # ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        label="Orages, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B1,
        label="Précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B2,
        label="Averses de grésil, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B3,
        label="Averses de grêle, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B5,
        label="Orages violents, neige",
    ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3,
    #     WWMF_SUBGRP.A4,
    #     label="Averses parfois neigeuses",
    #     r_min=3,
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3, WWMF_SUBGRP.A5, label="Orages ou averses", r_min=3
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3, WWMF_SUBGRP.B1, label="Précipitations verglaçantes ou
    #     averses", r_min=3
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3, WWMF_SUBGRP.B2, label="Averses avec parfois du grésil",
    #     r_min=3
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3, WWMF_SUBGRP.B3, label="Averses avec parfois de la grêle",
    #     r_min=3
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3, WWMF_SUBGRP.B4, label="Orages avec grêle ou averses",
    #     r_min=3
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A3, WWMF_SUBGRP.B5, label="Averses ou orages violents", r_min=3
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A4,
    #     WWMF_SUBGRP.A5,
    #     label="Orages, neige",
    #     r_min=3,
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A4,
    #     WWMF_SUBGRP.B1,
    #     label="Précipitations verglaçantes, neige",
    #     r_min=3,
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A4,
    #     WWMF_SUBGRP.B2,
    #     label="Giboulées neigeuses",
    #     r_min=3,
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A4,
    #     WWMF_SUBGRP.B3,
    #     label="Fortes giboulées neigeuses",
    #     r_min=3,
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A4,
    #     WWMF_SUBGRP.B4,
    #     label="Orages, giboulées neigeuses",
    #     r_min=3,
    # ),
    # *_sample_datasets(
    #     WWMF_SUBGRP.A4,
    #     WWMF_SUBGRP.B5,
    #     label="Orages violents, averses de neige",
    #     r_min=3,
    # ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        label="Précipitations verglaçantes ou orages",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        label="Orages ou averses de grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        label="Orages ou averses de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B4,
        label="Temps orageux avec grêle possible",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B5,
        label="Orages parfois violents",
    ),
    # >=3 TS family precipitation with 3 subgroups
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        label="Précipitations, parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        label="Précipitations, parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        label="Orages, précipitations, parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B1,
        label="Précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B2,
        label="Précipitations, temporairement avec grésil, ou neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B3,
        label="Précipitations, temporairement avec grêle, ou neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, pluie, mêlée de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses, pluie, mêlée de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        label="Averses, mêlées de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        label="Temps pluvieux avec orages",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B1,
        label="Pluie parfois verglaçante et averses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B2,
        label="Temps pluvieux avec averses de grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B3,
        label="Temps pluvieux avec averses de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B4,
        label="Temps pluvieux avec orages de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B5,
        label="Temps pluvieux avec orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        label="Orages, précipitations, parfois mêlées de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        label="Précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B2,
        label="Précipitations, temporairement avec grésil, ou neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B3,
        label="Précipitations, temporairement avec grêle, ou neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B4,
        label="Orages avec grêle, précipitations, temporairement neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B5,
        label="Orages violents, précipitations, temporairement neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        label="Pluie parfois verglaçante et orages",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        label="Pluie et orages parfois avec grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        label="Pluie et orages parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B4,
        label="Pluie et orages parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B5,
        label="Pluie et orages parfois violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        label="Pluie parfois verglaçante et averses de grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        label="Pluie parfois verglaçante et averses de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B4,
        label="Pluie parfois verglaçante et orages de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B5,
        label="Pluie parfois verglaçante et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        label="Pluie avec averses de grêle et de grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        label="Pluie avec averses de grésil et orages de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B5,
        label="Pluie avec averses de grésil et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Pluie avec averses et orages de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Pluie avec averses de grêle et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A1,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Pluie avec orages violents parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        label="Averses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        label="Orages, averses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B1,
        label="Précipitations parfois verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B2,
        label="Averses parfois de grésil, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B3,
        label="Averses parfois de grêle, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        label="Orages, averses, parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        label="Précipitations verglaçantes, neige prédominante",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B2,
        label="Averses de grésil, neige prédominante",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B3,
        label="Averses de grêle, neige prédominante",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige prédominante",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses, neige prédominante",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        label="Orages, précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        label="Fortes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B4,
        label="Fortes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B5,
        label="Orages violents, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        label="Précipitations parfois verglaçantes ou avec grésil, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        label="Précipitations parfois verglaçantes ou avec grêle, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B5,
        label="Orages violents, précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B5,
        label="Orages violents parfois avec grésil, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Fortes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Orages violents parfois avec grêle, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A2,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Orages, averses parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        label="Orages et averses parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        label="Précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B2,
        label="Giboulées neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B3,
        label="Fortes giboulées neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B5,
        label="Orages violents, averses parfois neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        label="Précipitations parfois verglaçantes et orages",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        label="Averses, parfois de grésil, et orages",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        label="Averses, parfois de grêle, et orages",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B4,
        label="Orages parfois avec grêle et averses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B5,
        label="Orages parfois violents et averses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        label="Précipitations parfois verglaçantes et averses de grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        label="Précipitations parfois verglaçantes et averses de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B4,
        label="Précipitations parfois verglaçantes et orages avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B5,
        label="Précipitations parfois verglaçantes et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        label="Averses, parfois de grésil ou de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        label="Averses, parfois de grésil et orages avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B5,
        label="Averses, parfois de grésil et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Averses et orages avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Averses parfois de grêle et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A3,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Averses et orages violents, parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        label="Orages, précipitations verglaçantes, averses de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        label="Orages parfois avec grésil, averses de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        label="Orages parfois avec grêle, averses de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B4,
        label="Orages parfois avec grêle, averses de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B5,
        label="Orages parfois violents, averses de neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        label="Précipitations parfois verglaçantes ou avec grésil, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        label="Précipitations parfois verglaçantes ou avec grêle, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B4,
        label="Orages avec grêle, précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B5,
        label="Orages violents, précipitations verglaçantes, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        label="Giboulées neigeuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A4,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses, neige",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        label="Précipitations verglaçantes et orages parfois avec grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        label="Précipitations verglaçantes et orages parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B4,
        label="Précipitations verglaçantes et orages parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes et orages parfois violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        label="Giboulées orageuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        label="Giboulées orageuses, parfois avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B5,
        label="Violentes giboulées orageuses",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Orages ou averses avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Orages, parfois violents et avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.A5,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Orages, parfois violents et avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        label="Précipitations verglaçantes et giboulées",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        label="Précipitations verglaçantes, averses de grésil et orages de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes, averses de grésil et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Précipitations verglaçantes, averses ou orages de grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes, averses de grêle et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes et orages violents avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Orages avec grêle et grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Orages parfois violents et grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Orages parfois violents et grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Orages violents avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        label="Précipitations verglaçantes, giboulées et orages avec grêle",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes, giboulées et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes, giboulées et orages violents",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Orages violents avec grêle et grésil",
    ),
    *_sample_datasets(
        WWMF_SUBGRP.B1,
        WWMF_SUBGRP.B2,
        WWMF_SUBGRP.B3,
        WWMF_SUBGRP.B4,
        WWMF_SUBGRP.B5,
        label="Précipitations verglaçantes, orages violents avec grêle et grésil",
    ),
]


class TestWWMFUtils:
    @pytest.mark.parametrize(
        "code,expected",
        [
            (49, True),
            (59, True),
            (85, True),
            (98, True),
            (99, True),
            (0, False),
            (50, False),
            (60, False),
        ],
    )
    def test_is_wwmf_severe(self, code, expected):
        assert is_wwmf_severe(code) == expected

    @pytest.mark.parametrize(
        "wwmfs,expected",
        [
            (30, True),
            (50, False),
            ([30, 31, 32, 38, 39], True),
            ([30, 31, 40, 38, 39], False),
        ],
    )
    def test_are_wwmf_visibilities(self, wwmfs, expected):
        if isinstance(wwmfs, List):
            assert are_wwmf_visibilities(*wwmfs) == expected
        else:
            assert are_wwmf_visibilities(wwmfs) == expected

    @pytest.mark.parametrize(
        "wwmfs,expected",
        [
            (40, True),
            (30, False),
            ([40, 50, 60, 70], True),
            ([41, 51, 61, 31], False),
        ],
    )
    def test_are_wwmf_precipitations(self, wwmfs, expected):
        if isinstance(wwmfs, List):
            assert are_wwmf_precipitations(*wwmfs) == expected
        else:
            assert are_wwmf_precipitations(wwmfs) == expected

    @pytest.mark.parametrize(
        "code,expected",
        [
            (58, True),
            (60, True),
            (61, True),
            (62, True),
            (63, True),
            (77, True),
            (78, True),
            (80, True),
            (81, True),
            (82, True),
            (83, True),
            (49, False),
            (70, False),
            (90, False),
        ],
    )
    def test_is_wwmf_snow(self, code, expected):
        assert is_wwmf_snow(code) == expected

    @pytest.mark.parametrize(
        "code,expected",
        [
            (40, True),
            (49, True),
            (50, True),
            (51, True),
            (52, True),
            (53, True),
            (58, True),
            (59, True),
            (70, True),
            (71, True),
            (72, True),
            (73, True),
            (77, True),
            (78, True),
            (93, True),
            (60, False),
            (80, False),
            (90, False),
        ],
    )
    def test_is_wwmf_rain(self, code, expected):
        assert is_wwmf_rain(code) == expected

    @pytest.mark.parametrize(
        "code,expected",
        [
            (70, True),
            (71, True),
            (72, True),
            (73, True),
            (77, True),
            (78, True),
            (80, True),
            (81, True),
            (82, True),
            (83, True),
            (84, True),
            (85, True),
            (92, True),
            (60, False),
            (90, False),
        ],
    )
    def test_is_wwmf_shower(self, code, expected):
        assert is_wwmf_shower(code) == expected

    @pytest.mark.parametrize(
        "code,expected",
        [
            (84, True),
            (85, True),
            (90, True),
            (91, True),
            (92, True),
            (93, True),
            (97, True),
            (98, True),
            (99, True),
            (60, False),
            (70, False),
            (80, False),
        ],
    )
    def test_is_wwmf_thunderstorm(self, code, expected):
        assert is_wwmf_thunderstorm(code) == expected

    @pytest.mark.parametrize(
        "codes,expected",
        [
            ([70], "Averses"),
            ([31, 50], "Brume et pluie"),  # Tests of concatenation
        ]
        + sample(dataset_wwmf_label, 200),
    )
    def test_wwmf_label(self, codes, expected):
        assert wwmf_label(*codes) == expected

    def test_wwmf_families(self):
        assert wwmf_families() == set()
        assert wwmf_families(30, 85, 78) == {
            WWMF_FAMILIES.VISIBILITY,
            WWMF_FAMILIES.SHOWER,
            WWMF_FAMILIES.SNOW,
            WWMF_FAMILIES.THUNDERSTORM,
            WWMF_FAMILIES.RAIN,
        }


class TestWWMF_SUBGRP:
    @pytest.mark.parametrize(
        "grp,expected",
        [
            (WWMF_SUBGRP.A1, True),
            (WWMF_SUBGRP.A2, True),
            (WWMF_SUBGRP.A3, True),
            (WWMF_SUBGRP.A4, True),
            (WWMF_SUBGRP.A5, True),
            (WWMF_SUBGRP.B1, False),
            (WWMF_SUBGRP.B2, False),
            (WWMF_SUBGRP.B3, False),
            (WWMF_SUBGRP.B4, False),
            (WWMF_SUBGRP.B5, False),
        ],
    )
    def test_is_A_group(self, grp, expected):
        assert grp.is_A_group == expected

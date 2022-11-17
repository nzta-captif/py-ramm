import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from shapely.geometry import Point

from pyramm.geometry import (
    build_partial_centreline,
    combine_continuous_segments,
    build_chainage_layer,
)


@pytest.mark.parametrize(
    "point,lengths,road_id,position_m",
    [
        (Point((172.608406, -43.451023)), {3656: None}, 3656, 179.462),
        (Point((172.608406, -43.451023)), {3656: None, 3654: None}, 3654, 241.879),
        (Point((172.608406, -43.451023)), {3656: [10, 100]}, 3656, 100),
        (Point((172.608406, -43.451023)), {3656: [200, None]}, 3656, 200),
        (Point((172.631957, -43.436542)), {1716: None}, 1716, 3371.371),
    ],
)
def test_build_partial_centreline(
    point, lengths, road_id, position_m, centreline, roadnames
):
    partial_centreline = build_partial_centreline(centreline, roadnames, lengths)
    position = partial_centreline.position(point)
    assert position["road_id"] == road_id
    assert round(position["position_m"], 3) == position_m


def test_combine_continuous_segments():
    df = pd.DataFrame(
        [
            {"road_id": 1, "start_m": 40, "end_m": 50},
            {"road_id": 1, "start_m": 50, "end_m": 60},
            {"road_id": 1, "start_m": 60, "end_m": 70},
            {"road_id": 1, "start_m": 100, "end_m": 110},
            {"road_id": 2, "start_m": 1000, "end_m": 1010},
            {"road_id": 2, "start_m": 1000, "end_m": 1010},  # test with duplicate row
            {"road_id": 2, "start_m": 1010, "end_m": 1020},
            {"road_id": 3, "start_m": 0, "end_m": 20},
        ]
    )
    expected = pd.DataFrame(
        [
            {"road_id": 1, "start_m": 40, "end_m": 70},
            {"road_id": 1, "start_m": 100, "end_m": 110},
            {"road_id": 2, "start_m": 1000, "end_m": 1020},
            {"road_id": 3, "start_m": 0, "end_m": 20},
        ]
    )
    new = combine_continuous_segments(df)
    assert_frame_equal(new, expected)


def test_combine_continuous_segments_groupby():
    df = pd.DataFrame(
        [
            {"road_id": 1, "start_m": 40, "end_m": 50, "c_surface_id": 1},
            {"road_id": 1, "start_m": 50, "end_m": 60, "c_surface_id": 1},
            {"road_id": 1, "start_m": 60, "end_m": 70, "c_surface_id": 2},
        ]
    )
    expected = pd.DataFrame(
        [
            {"road_id": 1, "start_m": 40, "end_m": 60, "c_surface_id": 1},
            {"road_id": 1, "start_m": 60, "end_m": 70, "c_surface_id": 2},
        ]
    )
    new = combine_continuous_segments(df, groupby=["road_id", "c_surface_id"])
    assert_frame_equal(new, expected)


def test_build_chainage_layer(centreline):
    df = build_chainage_layer(centreline, [3664, 3670, 3667])
    assert df[
        [
            "is_start",
            "is_end",
            "is_ramp",
            "is_2000s",
            "is_1000s",
            "is_500s",
            "is_200s",
            "is_100s",
            "label",
        ]
    ].to_dict("records") == [
        {
            "is_start": True,
            "is_end": False,
            "is_ramp": False,
            "is_2000s": False,
            "is_1000s": False,
            "is_500s": False,
            "is_200s": False,
            "is_100s": False,
            "label": "01S-0333/01.40-D",
        },
        {
            "is_start": False,
            "is_end": False,
            "is_ramp": False,
            "is_2000s": True,
            "is_1000s": True,
            "is_500s": True,
            "is_200s": True,
            "is_100s": True,
            "label": "01S-0333/02.00-D",
        },
        {
            "is_start": False,
            "is_end": False,
            "is_ramp": False,
            "is_2000s": False,
            "is_1000s": True,
            "is_500s": True,
            "is_200s": True,
            "is_100s": True,
            "label": "01S-0333/03.00-D",
        },
        {
            "is_start": False,
            "is_end": False,
            "is_ramp": False,
            "is_2000s": True,
            "is_1000s": True,
            "is_500s": True,
            "is_200s": True,
            "is_100s": True,
            "label": "01S-0333/04.00-D",
        },
        {
            "is_start": False,
            "is_end": True,
            "is_ramp": False,
            "is_2000s": False,
            "is_1000s": False,
            "is_500s": False,
            "is_200s": False,
            "is_100s": False,
            "label": "01S-0333/04.13-D",
        },
        {
            "is_start": True,
            "is_end": False,
            "is_ramp": True,
            "is_2000s": True,
            "is_1000s": True,
            "is_500s": True,
            "is_200s": True,
            "is_100s": True,
            "label": "01S-0333/00.00-R2",
        },
        {
            "is_start": False,
            "is_end": True,
            "is_ramp": True,
            "is_2000s": False,
            "is_1000s": False,
            "is_500s": False,
            "is_200s": False,
            "is_100s": False,
            "label": "01S-0333/00.25-R2",
        },
    ]

"""
create mask on grid from geometry

a offset of 0.5 is applied on xy coordinates
in order to balance the fact that
coordinates are truncated ( instead of rounded) by draw function
thus 0.9 is interpreted as 0 by draw
and 0.9 + 0.5 = 1.4 is interpreted as 1 by draw
"""
import json
from typing import Dict, Union
import numpy as np
from PIL.Image import new as PILnew
from PIL.ImageChops import logical_or as PILor
from PIL.ImageDraw import Draw as PILdraw
from shapely import geometry as shp_geom
from shapely.geometry import mapping as SHAmapping

import mfire.utils.mfxarray as xr

Shape = Union[
    shp_geom.Point,
    shp_geom.MultiPoint,
    shp_geom.LineString,
    shp_geom.MultiLineString,
    shp_geom.Polygon,
    shp_geom.MultiPolygon,
]


class GeoTypeException(Exception):
    """
    Exception on geometry Type
    """

    def __init__(self, key):
        self.message = "This geometry type is not managed : " + str(key)


class GeoDraw:
    """
    Draw geometry from json to image as mask
    """

    def __init__(self, grid_info: Dict):
        """
        drawer : link to image to draw
        grid : specification of grid represent by image
        """
        self.grid_info = grid_info
        self._set_image(
            PILnew("1", (self.grid_info["nb_c"], self.grid_info["nb_l"]))
        )  # actual image
        # link a type of geometry with action to do
        self.geoType_geoAction = {
            "Polygon": self._geopolygon,
            "MultiPolygon": self._geomultipolygon,
            "LineString": self._geoline,
            "MultiLineString": self._geomultiline,
            "Point": self._geopoint,
            "MultiPoint": self._geomultipoint,
        }

    def _set_image(self, image_in):
        self.image = image_in
        self.drawer = PILdraw(self.image)  # operator over image

    def get_image(self):
        return self.image

    def _lonlat2xy(self, coordinates):
        """
        convert latitude/longitude coordinates
        to list of x,y coordinates relative to grid
        Args :
        coordinates : list of points in geo coordinates
        Return :
        list of points in grid coordinates
        """
        LL = np.array(coordinates)
        A = self.grid_info["conversion_slope"]
        B = self.grid_info["conversion_offset"]
        X = A * LL + B
        # get all in one list
        return sum(X.tolist(), [])

    def draw_geo(self, geo):
        """
        manage the geometry of a geo
        select action to do by geometry type
        and apply it to the coordinate of the geometry
        """
        try:
            drawing = self.geoType_geoAction[geo["type"]]
        except KeyError as excpt:
            raise GeoTypeException(geo["type"]) from excpt
        drawing(geo["coordinates"])

    def draw_shape(self, shape):
        """
        Entry point to manage the geometry of a shape
        """
        geo = json.loads(json.dumps(SHAmapping(shape)))
        self.draw_geo(geo)

    def _geopolygon(self, lines):
        """
        Draw a polygon
        first line is the contour of poylgon
        other lines are inner holes of polygon (option)
        """
        contour = lines.pop(0)
        if len(lines) == 0:
            # draw a simple polygon
            self.drawer.polygon(self._lonlat2xy(contour), fill=1)
        else:
            # draw a polygon with inner holes
            # first working on a different image
            image_holes = PILnew("1", (self.grid_info["nb_c"], self.grid_info["nb_l"]))
            draw_holes = PILdraw(image_holes)
            # draw the outer polygon
            draw_holes.polygon(self._lonlat2xy(contour), fill=1)
            # remove inner holes with fill=0
            for inner in lines:
                draw_holes.polygon(self._lonlat2xy(inner), fill=0)
            # merge the previous image and the one with this polygon
            self._set_image(PILor(self.image, image_holes))

    def _geoline(self, line):
        """
        Draw a line
        width=2 to get continus line
        """
        self.drawer.line(self._lonlat2xy(line), fill=1, width=2)

    def _geopoint(self, point):
        """
        Draw a point as a list of (unique) points
        """
        self.drawer.point(self._lonlat2xy([point]), fill=1)

    def _geomultipolygon(self, geos):
        """
        Draw multipolygon, one by one as polygon
        """
        for geo in geos:
            self._geopolygon(geo)

    def _geomultiline(self, geos):
        """
        Draw multiline, one by one as line
        """
        for geo in geos:
            self._geoline(geo)

    def _geomultipoint(self, geos):
        """
        Draw multipoint, at once
        """
        self.drawer.point(self._lonlat2xy(geos), fill=1)

    def create_mask_PIL(self, poly: Shape) -> xr.Dataset:
        self.draw_shape(poly)

        dims = self.grid_info["dims"]
        name = self.grid_info["name"]

        ds = xr.Dataset()
        for x in list(dims):
            ds.coords[x] = self.grid_info[x]
        ds[name] = (dims, np.array(self.get_image()))
        # remove all unneeded coord
        ds = (
            ds.where(ds[name] > 0)
            .dropna(dim=dims[0], how="all")
            .dropna(dim=dims[1], how="all")
        )
        # to reduce time with computing operations
        ds[name] = ds[name].mask.bool
        return ds

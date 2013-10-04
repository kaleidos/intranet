# -*- coding: utf-8 -*-


class MapPosition(object):
    """Class to encapsulate a map point with latitude, longitude and a zoom
    factor.

    """

    def __init__(self, latitude, longitude, zoom=None):
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom

    def __unicode__(self):
        return u"%.6f, %.6f" % (self.latitude, self.longitude)



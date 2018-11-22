import math
from xml.etree import ElementTree
from datetime import datetime
from datetime import timedelta


class Point:
    R = 6372.795477598

    def __init__(self, lat, lon, time=None, speed=None):
        self.lat = float(lat)
        self.lon = float(lon)
        self.time = time
        self.speed = speed

    def get_distance(self, point):
        # Formula de Haversine en Km

        rad = math.pi / 180.0
        dlat = self.lat - point.lat
        dlon = self.lon - point.lon
        aux = (math.sin(rad * dlat / 2.0)**2) + \
              math.cos(rad * self.lat) * \
              math.cos(rad * point.lat) * \
              (math.sin(rad * dlon / 2.0))**2
        dist = 2.0 * self.R * math.asin(math.sqrt(aux))
        return dist

    def print(self):
        print(self.lat, self.lon)


class Segment:
    def __init__(self, p1, p2, star_index, end_index):
        self.p1 = p1
        self.p2 = p2
        self.star_index = star_index
        self.end_index = end_index

    def check_point_inside(self, point):
        # Comprueba si el punto está dentro del segmento.

        if self.p1.lat <= point.lat <= self.p2.lat and self.p1.lon <= point.lon <= self.p2.lon:
            return True
        else:
            return False


class Track:
    THRESHOLD_DISTANCE_DETECTION = 0.01
    SEGMENT_DISTANCE = 0.5
    SPEED_THRESHOLD_DETECTION = 1.5

    def __init__(self):
        self.name = ""
        self.time = ""
        self.trkLst = []
        self.segLst = []
        self.duration = timedelta()
        self.duration_movement = timedelta()
        self.filename = ""

    def load_gpx(self, filename):
        # Carga un track desde un fichero GPX

        self.filename = filename
        xmldoc = ElementTree.parse(filename)
        root = xmldoc.getroot()

        ns = root.tag.split('}')[0].strip('{').strip()
        if len(ns) > 0:
            trkpt_tag = "{" + ns + "}trkpt"
            time_tag = "{" + ns + "}time"
            name_tag = "{" + ns + "}name"
        else:
            trkpt_tag = "trkpt"
            time_tag = "time"
            name_tag = "name"

        for n in root.iter(name_tag):
            self.name = n.text

        time_ref = None
        speed = 0
        self.duration = timedelta()
        self.duration_movement = timedelta()
        last_point = None
        delta_time = timedelta()
        for xml_point in root.iter(trkpt_tag):
            lat = float(xml_point.attrib["lat"])
            lon = float(xml_point.attrib["lon"])
            time = datetime.strptime(xml_point.find(time_tag).text, "%Y-%m-%dT%H:%M:%S.000Z")

            if time_ref is not None:
                delta_time = time - time_ref
                self.duration = self.duration + delta_time
                dist = last_point.get_distance(Point(lat, lon))
                if delta_time.total_seconds() > 0:
                    speed = dist / (delta_time.total_seconds() / 60 / 60)
                else:
                    speed = 0

            if speed > self.SPEED_THRESHOLD_DETECTION:
                self.duration_movement = self.duration_movement + delta_time

            time_ref = time
            last_point = Point(lat, lon, time, speed)

            self.trkLst.append(last_point)

        self.generate_segments()
        return

    def generate_segments(self):
        # Genera los segmentos de detección rápida.

        self.segLst = []
        star_index = 0
        end_index = 0
        lat1 = None
        lon1 = None
        lat2 = None
        lon2 = None
        for s in self.trkLst:
            if lat1 is None or s.lat < lat1:
                lat1 = s.lat
            if lon1 is None or s.lon < lon1:
                lon1 = s.lon
            if lat2 is None or s.lat > lat2:
                lat2 = s.lat
            if lon2 is None or s.lon > lon2:
                lon2 = s.lon

            p1 = Point(lat1, lon1)
            p2 = Point(lat2, lon2)

            if p1.get_distance(p2) > self.SEGMENT_DISTANCE:
                self.segLst.append(Segment(p1, p2, star_index, end_index))
                lat1 = None
                lon1 = None
                lat2 = None
                lon2 = None
                star_index = end_index + 1

            end_index = end_index + 1

        if lat1 is not None:
            self.segLst.append(Segment(p1, p2, star_index, end_index - 1))

    def compare_full_track(self, track):
        # Compara los tracks e indica el porcentaje de coincidencia. Lento

        success = 0.0
        error = 0.0
        found = False

        if len(self.trkLst) >= len(track.trkLst):
            track1 = self
            track2 = track
        else:
            track1 = track
            track2 = self

        for i in track1.trkLst:
            found = False
            for j in track2.trkLst:
                if i.get_distance(j) < self.THRESHOLD_DISTANCE_DETECTION:
                    found = True
                    break
            if found:
                success = success + 1
            else:
                error = error + 1

        percentage = (100.0 * success) / len(self.trkLst)
        return percentage

    def compare_segmented_track(self, track):
        # Compara los tracks e indica el porcentaje de coincidencia. Rápido

        success = 0.0
        error = 0.0
        found = False

        if len(self.trkLst) >= len(track.trkLst):
            track1 = self
            track2 = track
        else:
            track1 = track
            track2 = self

        for i in track1.trkLst:
            found = False
            for j in track2.segLst:
                if j.check_point_inside(i):
                    for i_pnt in range(j.star_index, j.end_index + 1):
                        if i.get_distance(track2.trkLst[i_pnt]) < self.THRESHOLD_DISTANCE_DETECTION:
                            found = True
                            break
                if found:
                    break
            if found:
                success = success + 1
            else:
                error = error + 1

        percentage = (100.0 * success) / len(self.trkLst)
        return percentage

    def print(self):
        print(self.name, self.time)
        for i in self.trkLst:
            i.print()

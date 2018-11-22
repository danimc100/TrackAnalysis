from TrackLib import Track
from TrackLib import Point
import time
from datetime import datetime
import glob


def datetime_test():
    d1 = datetime(2018, 11, 15, 22, 0, 0, 0)
    d2 = datetime(2018, 11, 15, 22, 30, 0, 0)
    d3 = d2 - d1


def read_xml_test():
    star = time.time()

    anillo = Track()
    anillo.load_gpx("Data/AnilloVerde.gpx")

    elapse = time.time() - star
    print("Read XML Tiempo:", elapse)


def test_compare_track():
    print("Leyendo archivos GPX")
    trk1 = Track()
    trk1.load_gpx("Data/MadridTitulciaMadrid.gpx")
    # trk1.load_gpx("Data/Madrid-Villaconejos-Madrid2.gpx")

    trk2 = Track()
    # trk2.load_gpx("Data/MadridTitulciaMadrid.gpx")
    trk2.load_gpx("Data/MadridVillacomejosMadrid.gpx")
    # trk2.load_gpx("Data/Soto-Canencia-Navafria-Morcuera-Soto.gpx")

    print("Puntos trk1:", len(trk1.trkLst))
    print("Puntos trk2:", len(trk2.trkLst))

    for sd in range(1, 100, 5):
        star = time.time()
        sd_aux = sd / 100.0
        trk1.SEGMENT_DISTANCE = sd_aux
        trk2.SEGMENT_DISTANCE = sd_aux
        star_time_gs = time.time()
        trk1.generate_segments()
        trk2.generate_segments()
        elapse_time_gs = time.time() - star_time_gs
        print("compare_segmented_track:", trk2.compare_segmented_track(trk1), end=" ")
        elapse = time.time() - star
        print("SD: ", sd_aux, end=" ")
        print("Tiempo:", elapse, end=" ")
        print("Tiempo GenSeg:", elapse_time_gs)

    p1 = Point(40.385232, -3.717565, None)
    p2 = Point(40.397629, -3.715830, None)
    print("Distancia: ", p1.get_distance(p2))


def analysis_track_test():
    for f in glob.glob("DataBulk/*.gpx"):
        print(f)

    filename_base = "DataBulk/2018-11-11T08:00:32+00:00_3153503214.gpx" # Madrid-Titulcia-Madrid
    #filename_base = "DataBulk/2018-11-09T08_04_40+00_00_3149100690.gpx" # Madrid-Villaconelos-Madrid

    track_base = Track()
    track_base.load_gpx(filename_base)

    for f in glob.glob("DataBulk/*.gpx"):
        if f != filename_base:
            track = Track()
            track.load_gpx(f)
            percentage = track_base.compare_segmented_track(track)
            if percentage > 50:
                print("%s -> %s %f "%(track.filename,track.name,percentage))
            # if track_base.compare_segmented_track(track) > 90:
              #   print(f)


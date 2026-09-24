"""Create a QGIS-ready working layer from the 2018 Jounan CSV2.

The CSV's geographic coordinates are provisionally interpreted as Tokyo Datum
(EPSG:4301). GDAL's available Tokyo to WGS 84 operation is EPSG:15484
(nominal accuracy 9 m). This is a working interpretation, not source metadata.
Run with a Python environment containing GDAL's osgeo bindings.
"""

import csv
from pathlib import Path

from osgeo import gdal, ogr, osr


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/naisui_poc/01_raw/hazard_map/tokyo_opendata_jonankaisei/3_jonankaiseicsv2.csv"
OUTPUT = ROOT / "data/naisui_poc/02_processed/evaluation/jonankaisei_csv2_tokyo_datum_working.gpkg"
LAYER = "jonankaisei_csv2_tokyo_datum_working"


def spatial_ref(epsg):
    ref = osr.SpatialReference()
    ref.ImportFromEPSG(epsg)
    ref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return ref


def main():
    gdal.UseExceptions()
    ogr.UseExceptions()
    osr.UseExceptions()
    source_crs = spatial_ref(4301)
    target_crs = spatial_ref(4326)
    transform = osr.CoordinateTransformation(source_crs, target_crs)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
    driver = ogr.GetDriverByName("GPKG")
    dataset = driver.CreateDataSource(str(OUTPUT))
    layer = dataset.CreateLayer(LAYER, target_crs, ogr.wkbPoint, options=["SPATIAL_INDEX=YES"])
    for name, kind in [
        ("source_row", ogr.OFTInteger),
        ("depth_m", ogr.OFTReal),
        ("ground_elevation_m", ogr.OFTReal),
        ("source_lat", ogr.OFTReal),
        ("source_lon", ogr.OFTReal),
    ]:
        layer.CreateField(ogr.FieldDefn(name, kind))

    count = 0
    layer.StartTransaction()
    with SOURCE.open("r", encoding="cp932", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for row_number, row in enumerate(reader, start=2):
            depth, elevation, lat, lon = map(float, row[:4])
            x, y, _ = transform.TransformPoint(lon, lat)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("source_row", row_number)
            feature.SetField("depth_m", depth)
            feature.SetField("ground_elevation_m", elevation)
            feature.SetField("source_lat", lat)
            feature.SetField("source_lon", lon)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint_2D(x, y)
            feature.SetGeometry(point)
            layer.CreateFeature(feature)
            feature = None
            count += 1
            if count % 10000 == 0:
                layer.CommitTransaction()
                layer.StartTransaction()
    layer.CommitTransaction()
    dataset = None
    print(f"Created {OUTPUT} with {count} points")


if __name__ == "__main__":
    main()

# mkvirtualenv gee1
# setprojectdir .
# pip install flask
# deactivate
# workon gee1
# pip install folium
# pip install earth-engine api
# earthengine authenticate
# python test1.py


from flask import Flask, render_template, request
import ee
import folium
import json
from datetime import date


app = Flask(__name__)
ee.Initialize()

EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'
token_mapbox = "pk.eyJ1IjoiZWVtdXE5NiIsImEiOiJjanh3c3I1b3cwNXVnM21wamx0YWVmNjE0In0.Rz8bEgOFOuSedCL-qPIkLQ"
# tileurl = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(token_mapbox)
tileurl = 'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/tiles/256/{z}/{x}/{y}?access_token=' + str(
    token_mapbox)


def Mapdisplay(center, dicc, Tiles="OpensTreetMap", zoom_start=10):
    mapViz = folium.Map(location=center, tiles=Tiles, zoom_start=zoom_start)
    # mapViz = folium.Map(location=center,tiles=Tiles, zoom_start=zoom_start) tiles = "OpensTreetMap" in argument
    folium.TileLayer(tiles=tileurl, attr='Mapbox', overlay=True,
                     name='satellite view').add_to(mapViz)
    for k, v in dicc.items():
        if ee.image.Image in [type(x) for x in v.values()]:
            folium.TileLayer(
                tiles=EE_TILES.format(**v),
                attr='Google Earth Engine',
                overlay=True,
                name=k
            ).add_to(mapViz)
        else:
            folium.GeoJson(
                data=v,
                name=k
            ).add_to(mapViz)
    mapViz.add_child(folium.LayerControl())
    return mapViz


def getGeometryCoordinates(geometry):
    s = geometry[2:-2]
    coordinatesList = s.split('],[')
    length = len(coordinatesList)
    finalList = []
    for i in range(0, length):
        sub = coordinatesList[i]
        latlngString = sub
        latLngList = latlngString.split(',')
        lat = float(latLngList[0])
        lng = float(latLngList[1])
        list1 = [lng, lat]
        finalList.append(list1)
    coordinatesFinalList = []
    finalList.append(finalList[0])
    coordinatesFinalList.append(finalList)
    return coordinatesFinalList


def iter(image, newlist):
    date = image.date().format('dd MMM YYYY')
    newlist = ee.List(newlist)
    return ee.List(newlist.add(date))


def datesList(imgcol):
    return imgcol.iterate(iter, ee.List([]))


@app.route("/")
def hello():
    return "Please use /ndvi or /dates"


@app.route("/ndvi", methods=['GET'])
def show_map():
    s = request.args.get('geometry')
    start_date = request.args.get('date')
    today = date.today()

    datetoday = today.strftime("%Y-%m-%d")
    coordinatesFinalList = getGeometryCoordinates(s)
    polygon = ee.Geometry.Polygon(coordinatesFinalList)

    collection = ee.ImageCollection(
        'COPERNICUS/S2').filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)
    collection = collection.filterDate(
        start_date, datetoday).filterBounds(polygon)
    imageList = collection.toList(50)

    palette = ['FFFFFF', 'D1DAD7', 'EE5E5A', 'F80406', 'FF4404', 'FEA406', 'FCDA00', 'C5ED03',
               '9CD804', '73CA05', '57BA00', '3FA80C', '2BA903', '029D04', '009600', '018304', '027802']

    vizParams = {'min': 0, 'max': 1, 'palette': palette}

    img = ee.Image(imageList.get(0))
    my_area = img.clip(polygon)
    ndvi = my_area.normalizedDifference(['B8', 'B4'])
    mapId = ndvi.getMapId(vizParams)

    center0 = coordinatesFinalList[0]
    center1 = center0[0]
    center = [center1[1], center1[0]]

    m = Mapdisplay(center, {'NDVI': mapId}, zoom_start=17)
    # m.add_child(folium.ClickForMarker())

    html_map = m.get_root().render()
    return html_map
    # return HttpResponse(str(coordinatesFinalList))


@app.route("/dates", methods=['GET'])
def get_dates():

    s = request.args.get('geometry')
    start_date = request.args.get('date')
    today = date.today()

    datetoday = today.strftime("%Y-%m-%d")
    coordinatesFinalList = getGeometryCoordinates(s)
    polygon = ee.Geometry.Polygon(coordinatesFinalList)

    collection = ee.ImageCollection(
        'COPERNICUS/S2').filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)
    collection = collection.filterDate(
        start_date, datetoday).filterBounds(polygon)
    data = {}
    data['dates'] = datesList(collection).getInfo()
    json_data = json.dumps(data)
    return json_data


@app.route("/stat", methods=['GET'])
def get_stats():
    s = request.args.get('geometry')
    start_date = request.args.get('date')

    coordinatesFinalList = getGeometryCoordinates(s)
    polygon = ee.Geometry.Polygon(coordinatesFinalList)
    today = date.today()

    datetoday = today.strftime("%Y-%m-%d")

    collection = ee.ImageCollection(
        'COPERNICUS/S2').filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10)
    collection = collection.filterDate(
        start_date, datetoday).filterBounds(polygon)
    imageList = collection.toList(10)
    img = ee.Image(imageList.get(0))
    my_area = img.clip(polygon)
    ndvi = my_area.normalizedDifference(['B8', 'B4'])

    count = ndvi.reduceRegion(ee.Reducer.count(), polygon, 10)
    mean = ndvi.reduceRegion(ee.Reducer.mean(), polygon, 10)
    median = ndvi.reduceRegion(ee.Reducer.median(), polygon, 10)
    std = ndvi.reduceRegion(ee.Reducer.stdDev(), polygon, 10)
    data = {}
    data['date'] = start_date
    data['count'] = count.values().get(0).getInfo()
    data['mean'] = mean.values().get(0).getInfo()
    data['median'] = median.values().get(0).getInfo()
    data['std'] = std.values().get(0).getInfo()
    json_data = json.dumps(data)
    return json_data


if __name__ == "__main__":
    app.run()

from bson import json_util, objectid
from flask import Flask, g, render_template, request, Response, send_from_directory
import json
import os
from pymongo.mongo_client import MongoClient

app = Flask(__name__)
app.config.from_pyfile('conveniences.cfg')
conf = app.config
app.static_url_path = conf['STATIC_URL_PATH'] if conf['STATIC_URL_PATH'] else ''

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/<path:resource>')
def serve_static_resource(resource):
    return send_from_directory('static/', resource)

def get_db():
    if not hasattr(g, 'mongodb_client'):
        g.mongodb_client = get_MongoDB()
    return g.mongodb_client

# This does not work with Python 3
#@app.teardown_appcontext
#def close_db(error):
#    """Closes the database again at the end of the request."""
#    if hasattr(g, 'mongodb_client'):
#        g.mongodb_client.close()

def get_MongoDB():
    client = MongoClient(conf['DB_HOST'], conf['DB_PORT'])
    if conf['DB_USER']:
        client[conf['DB_NAME']].authenticate(conf['DB_USER'], conf['DB_PASS'], source='admin')
    db = client[conf['DB_NAME']]
    return db

@app.route("/ws/toilets/within")
def within():
    db = get_db()

    # Get boundary coords - production code would check for invalid values
    lat1 = float(request.args.get('lat1'))
    lon1 = float(request.args.get('lon1'))
    lat2 = float(request.args.get('lat2'))
    lon2 = float(request.args.get('lon2'))

    # Make GeoJSON box
    geometry = { "type" : "Polygon", "coordinates" : [[[lon1, lat1], [lon2, lat1], [lon2, lat2], [lon1, lat2], [lon1, lat1]]]}
    # Limit results for large datasets 
    result = db.toilets.find({"geometry.coordinates" : { "$geoWithin" : { "$geometry" : geometry} } }).limit(conf['RESULT_LIMIT'])
    return Response(response=str(json.dumps({'results':list(result)},default=json_util.default)), status=200, mimetype="application/json" )

@app.route("/ws/toilets/near")
def near():
    db = get_db()
    # Get request parameters - production code would check for invalid values
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    # Limit results in case dataset is large
    result = db.toilets.find({"geometry.coordinates" : { "$near" : {"$geometry" : { "type" : "Point" , "coordinates": [ lon , lat ] }}}}).limit(conf['RESULT_LIMIT'])

    # Convert results into valid JSON
    return Response(response=str(json.dumps({'results':list(result)},default=json_util.default)), status=200, mimetype="application/json" )

@app.route("/ws/toilets")
def all_toilets():
    db = get_db()

    result = db.toilets.find().limit(conf['RESULT_LIMIT'])
    return Response(response=str(json.dumps({'results':list(result)},default=json_util.default)), status=200, mimetype="application/json" )

if __name__ == "__main__":
    app.run()

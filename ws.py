from flask import Flask
from flask import g
from flask import Response
from flask import request
from flask import render_template
import os
from pymongo.mongo_client import MongoClient
import json
from bson import json_util
from bson import objectid

# Define location of static content
app = Flask(__name__, static_url_path='' )
# Don't let Flask swallow error messages
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def index():
    return app.send_static_file("index.html")

# Database setup

def get_db():
    if not hasattr(g, 'mongodb_client'):
        g.mongodb_client = get_MongoDB()
    return g.mongodb_client


def get_MongoDB():
    client = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_HOST'],  int(os.environ['OPENSHIFT_MONGODB_DB_PORT']))
    client[os.environ['OPENSHIFT_APP_NAME']].authenticate(os.environ['OPENSHIFT_MONGODB_DB_USERNAME'], os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'], source='admin')
    db = client[os.environ['OPENSHIFT_APP_NAME']]
    return db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
if hasattr(g, 'mongodb_client'):
    g.mongodb_client.close()

# Endpoints 

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
    result = db.toilets.find({"geometry.coordinates" : { "$geoWithin" : { "$geometry" : geometry} } }).limit(800)
    return Response(response=str(json.dumps({'results':list(result)},default=json_util.default)), status=200, mimetype="application/json" )

@app.route("/ws/toilets/near")
def near():
    db = get_db()
    # Get request parameters - production code would check for invalid values
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    # Limit results in case dataset is large
    result = db.toilets.find({"geometry.coordinates" : { "$near" : {"$geometry" : { "type" : "Point" , "coordinates": [ lon , lat ] }}}}).limit(200)

    # Convert results into valid JSON
    return Response(response=str(json.dumps({'results':list(result)},default=json_util.default)), status=200, mimetype="application/json" )

@app.route("/ws/toilets")
def all_toilets():
    db = get_db()

    result = db.toilets.find().limit(200)
    return Response(response=str(json.dumps({'results':list(result)},default=json_util.default)), status=200, mimetype="application/json" )

if __name__ == "__main__":
    app.run()

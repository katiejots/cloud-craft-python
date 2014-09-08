# Map of Public Conveniences in Wellington 
*powered by Flask, Python, MongoDB, and Leaflet.js*

To deploy a clone of this application using the [`rhc` command line tool](http://rubygems.org/gems/rhc):

    rhc app create conveniences python-2.7 mongodb-2.4 --from-code=https://github.com/codemiller/cloud-craft-python.git -s
    
Or [link to a web-based clone+deploy](https://openshift.redhat.com/app/console/application_type/custom?cartridges%5B%5D=python-2.7&scale=true&cartridges%5B%5D=mongodb-2&initial_git_url=https%3A%2F%2Fgithub.com%2Fcodemiller%2Fcloud-craft-python.git) on [OpenShift Online](http://OpenShift.com) or on [your own OpenShift cloud](http://openshift.github.io): 

    https://openshift.redhat.com/app/console/application_type/custom?cartridges%5B%5D=python-2.7&scale=true&cartridges%5B%5D=mongodb-2&initial_git_url=https%3A%2F%2Fgithub.com%2Fcodemiller%2Fcloud-craft-python.git

A demo is available at: [http://conveniences-cloudcraft.rhcloud.com/](http://conveniences-cloudcraft.rhcloud.com/)

## Local Development

To run the application locally, install Python, MongoDB 2.4 or higher, and the required Python modules in _setup.py_ (these can be installed using [Pip](http://en.wikipedia.org/wiki/Pip_\(package_manager\)), eg: `sudo pip install Flask && sudo pip install pymongo`). Alternatively, you could use `rhc port-forward` and set the database connection parameters in _conveniences.cfg_ to point to the instance of MongoDB hosted on OpenShift.

Make sure MongoDB is running, and add the data and index with commands such as the following: 

	mongoimport -d conveniences -c toilets --type json --file wellington-city-public-conveniences.json
	mongo conveniences --eval 'db.toilets.ensureIndex( { "geometry.coordinates" : "2dsphere" } )'

Check that the default DB connection parameters in _conveniences.cfg_ match your locally running MongoDB instance.

Run the app on localhost with the following command:

    python app.py

## License
This code is dedicated to the public domain to the maximum extent permitted by applicable law, pursuant to CC0 (http://creativecommons.org/publicdomain/zero/1.0/)

Toilet icon by [Ben Hoad](http://twitter.com/benhoad).

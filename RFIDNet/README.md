
# Project RFIDSim
---

## About the project

In today's world, real-time location data are simultaneously more available and more valuable than ever.  We rarely think about the complex and interconnected ways that the devices we use are constanty interacting with the world around us.  Few people would be surprised to learn that modern smart vehicles, for example, are constantly communicating with nearby infrastructure using established communication protocols, letting nearby traffic signaling equiptment know the vehicle's precise GPS location, bearing, and even whether the windshield wipers are on. [citation 1]  In return, vehicles recieve information like the signal phase of nearby traffic lights. [2]

The silent communication network surrounding us also has an increasing number of nodes related to RFID technology.  RFID chips and scanners span a huge range of types and complexites, and an even wider range of uses.  We are used to seeing these chips, which are small enough to hide under stickers, on the products we buy, the ATM cards we use, and even embedded in the flesh of our pets.  RFID chips can be passive or active, but most are passive - they have no power source, and thus function using only the energy transmitted from a scanner to power an internal antenna, which returns a payload of information.  Therefore, the range at which a chip can be read depends mostly on the power transmitted from the reader, and its sensitivity to returned signals.  RFID chip readers can be classified into three categories:

1. Low Frequency: 125 kHz. and 134.3 kHz.  These types of readers are used for things like ATM transactions, and typically only have a range of a couple feet at most. [2]
2. High Frequency: ~13.56 MHz.  These types of readers might be used in theft-prevention settings, for example, and operate at a range of a few meters at most. [2]
3. Ultra High Frequency & Super High Frequency: up to 2.45 GHz.  These types of tags are typically paired with active tags, and might be used for vehicle applications, or industrial asset management.  Many have a 100m range, and remarkably, some readers can even pick up a signal up to 3km away. [2]

The applications for this technology are endless.  In the field of logistics, in particular, companies are willing to pay for real-time insights that help guide business decisions.  As there is no centralized infrastructure to track RFID chips, a decentralized approach is gaining popularity.  Some companies, such as COIN, provide a keychain RFID reader that connect to your phone via bluetooth. [3] When carrying it around, it scans nearby chips, which are authenticated on a decentralized blockchain.  Companies that pay for the data provide value that is paid out to users. For example, FedEx might buy information about the realtime location of packages and vehicles, which would be payed out to users who happened to scan the chips linked to those objects.

As the RFID scanner network grows, tools will be needed to identify gaps and areas of need.  This app randomly generates start and endpoints in a study area, and generates driving routes between them.  This is meant to simulate the virtually random routes taken by logistics companies as they make deliveries to addresses that vary day to day.  The app allows you to propose a location for a given reader placement, and then run a simulation of hypothetical delivery routes - as delivery vehicles are guarunteed to contain countless RFID chips.  The number of routes that pass within each proposed reader's range are returned as a report.

The app is built using entirely free and open-source tools, as detailed below.


## Installation & setup

Video: [https://youtu.be/1GI-2vKO760](https://youtu.be/1GI-2vKO760)


## Installation & setup

This app consists of a GeoDjango web application, PostGIS database (an extension of PostGreSQL), and a OSRM http server that provides street network routing.  Each componenet is configured to run in a separate Docker container, which has the benefits of easier deplyment and scalability.  

**Deployment instructions:**
1. Download and unzip the clogan_final.zip package.
2. Ensure that Docker Desktop is installed, and requirements (such as vmmem for Windows) are met.  This was tested with Docker Desktop for Windows v4.17.0
3. In the root directory, find docker-compose.yml.  At time of build, here are component specs, from Docker:
- PostgreSQL 16.1 (Debian 16.1-1.pgdg110+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1
4. In command prompt / terminal, navigate to the root directory, and run command:
    docker-compose up
5. This should create 4 docker containers: the GeoDjango web application, PostGIS, adminer for db management, and OSRM.  The final component will take the longest to build, since it will download the roughly 1.4GB data spanning the US Northeast region, process it, and built it into a functioning street network or "graph."  This takes just under 16 minutes to build on my 8-core machine with 32GB of RAM.  Thank you for your patience!
6. Once everything is built, migrations still need to be run.  In Docker desktop, open the terminal for the GeoDjango machine.  Run the following:
    python manage.py migrate
7. Once this completes successfully, run the following.  Specifying to run on default route (0.0.0.0:8000) makes the server accessible from the host machine.
    python manage.py runserver 0.0.0.0:8000
8. This will start the server, which should be accessible by navigating to the following URL:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
9. To create a simulation, first register a user.  On the Home page or my Simulations page, click the New Simulation button.  
10. This will take you to a spatial ModelForm.  To add a point to the map, select the pointer/marker icon, then click on the map.  Next, select the class, which determines the range of the reader.  Click submit.
11. Now you are taken to a view of your proposed RFID readers, and their ranges.  To add additional readers, click Add Another Reader, and repeat as many times as you like.
12. When you are ready to run the simulation, click Run Simulation.  100 routes will be generated at random, and a report will be returned that includes the number of routes that could have been read by each proposed reader.

## Included files and components

**GeoDjango** - This extension to Django makes it easy to build a GIS web application.  It offers APIs to easily store spatial information in model fields, and perform analysis.  It extends the QuerySet api so that you can perform Spatial Lookups on spatial model fields.
**GDAL / GEOS / PROJ** - These GIS libraries are required for GeoDjango.  They should be installed by the web app Dockerfile, but installation issues are common given that these are 3rd party libraries.  Errors referencing GEOS or GDAL can be resolved using the GeoDjango documentation:
[https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/)
**OSRM** - This component was most challeging to pick and get acquainted with.  Many open-source routing solutions exist, so picking one can be daunting.  This solution was chosen because it has a relatively quick and easy setup process, and is easy to use over a simple http interface. Most other solutions require extensive data creation and pre-processing, whereas OSRM can use OpenSteetMaps data out-of-the-box (although I'm sure some additional pre-processing would imporve results).
**OpenStreetMaps - Geofabrik** - Detailed street data is not readily available for free in most places.  OpenStreetMaps solves that problem by crowdsourcing data from users.  It really is the holy grail of crowdsouced GIS data.  Geofabrik provides a free, easy, and up-to-date download of any given region or subregion of the world.
**PostGIS** - PostGIS, the GIS extension for PostGreSQL, is really the best open source spatial database.  It is widely compatible, and has extensive spatial functionality.
**leaflet** - Leaflet is a great open source choice for displaying maps on a web page.  It is fairly easy to use, and comes in the django-leaflet python package (included in requirements.txt) that integrates into GeoDjango exceptionally well - allowing us to use spatial ModelForms and providing widgets for creating and editing spatial data. GeoDjango also gives us some leaflet Javascript tools to manipulate web maps.
**leaflet-ajax** - This open source third-party tool is a little old, but its very helpful for adding data to a leaflet map.  It is downloaded to the static directory.
**Bootstrap** - The best.


## Design decisions

- Open Source: The decision to use entirely open source development tools was made.  While GIS tools from companies like Google and Esri can be extremely convenient, work out-of-the-box, and have lots of bells and whistles, there are also downsides to those types of products, the most obvious being cost.  A less obvious reason to use open source software is compatibility and reproducibility.  Anyone, anywhere can recreate this project, and open source data geospatial data formats are largely compatible with each other, while proprietary formats may be harder to convert.
- Study Area: The decision to limit the study area for this project to the area around Cambridge, MA was made.  This is essentially arbitrary, though living in Cambridge and turning this in for a Harvard course tipped the scales.
- Coordinate Reference System (CRS): The CRS, or spatial reference system, EPSG:3857 was chosed for the spatial Model Fields in this project.  This CRS is commonly used for web mapping, and was the most convenient choice because it is the CRS of most map tiles, and it makes it easy to add layers to the map and perform analysis when they all match.  This CRS also uses meters, which is convenient.  One challenge this presented was the need to convert other data, such as coordinates and OSRM routes from WGS84 (EPSG: 4326).

**Areas for future improvement**
- Custom study area: In the future, it would be great if there was a way for users to define their own study area.  This could be done by drawing an extent polygon, entering a bounding box, or using the viewframe extent.
- Custom route count: It would also be great to allow users to add a custom count of routes to be returned as part of the simulation.  This could easily be implemented following the same design pattern as the Chip Class selection.
- Buffer popups: A usability concern is that it's hard to tell which reader on the map corresponds to which row on the table.  Adding popups using leaflet would be a great solution.  

Again, due to the time constraints of this project, not all these ideas could be implemented.  There's always more to do!


## Noteworthy sources & citations

**In-text citations**
1. SAE communication standards, ANSI website https://webstore.ansi.org/standards/sae/sae27352020
2. DOT explanation of Connected Vehicles (CV): https://www.transportation.gov/research-and-technology/how-connected-vehicles-work
3. RFID types and read ranges https://skyrfid.com/RFID_Range.php
4. COIN readers https://coinapp.co/sentinelx/ble

**Other citations**
- GeoDjango reference: https://docs.djangoproject.com/en/dev/ref/contrib/gis/
- OSRM GitHub page: https://github.com/Project-OSRM/osrm-backend/tree/master
- Geofabrik download page for US Northeast: https://download.geofabrik.de/north-america/us-northeast.html
- django-leaflet doc: https://django-leaflet.readthedocs.io/en/latest/index.html
- leaflet-ajax library: https://github.com/calvinmetcalf/leaflet-ajax/tree/gh-pages
- Coordinate Reference System EPSG:3857: https://epsg.io/3857

**Blogs, posts, etc.**
- Useful guide for OSRM deployment on Windows: https://gist.github.com/AlexandraKapp/e0eee2beacc93e765113aff43ec77789
- Guide I followed for turning an array of JSON dicts into a table: https://www.valentinog.com/blog/html-table/
- Blogpost on GeoDjango + leaflet that served as inspiration: https://medium.com/@aminbobekeur/leaflet-django-geodjango-example-b07ff4bc25e8
- Helpful SO post that served as a guide for my OSRM Dockerfile: https://stackoverflow.com/questions/70135716/openstreetroutingmap-docker/70663481#70663481


import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.gis import geos
from django.contrib.gis.geos import LineString
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.core.serializers import serialize
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import RFIDForm
from .models import ChipBuffer, RFIDReader, Route, Simulation, User
    

def index(request):
    '''Render the homepage'''
    return render(request, "rfid_sim/index.html")

@csrf_exempt
@login_required
def view_simulation(request, sim_id):
    '''Render the simulation page with option for form'''
    form = RFIDForm()
    sim_run = Simulation.objects.get(pk=sim_id).run
    return render(request, "rfid_sim/simulation.html", {
        "rfid_form": form,
        "sim_id": sim_id,
        "sim_run": sim_run
    })


@csrf_exempt
@login_required
def create_simulation(request):
    new_sim = Simulation()
    user = User.objects.get(pk=request.user.id)
    new_sim.owner = user
    new_sim.save()
    sim_id = new_sim.id
    return HttpResponseRedirect(f'/simulations/{sim_id}')


@login_required
def my_simulations(request):
    '''Render My Simulations page with a list of owned simulations'''
    sim_list = User.objects.get(pk=request.user.id).owned_sims.all()
    return render(request, 'rfid_sim/my_simulations.html', {
        "sim_list": sim_list,
    })


@csrf_exempt
@login_required
def create_chip_reader(request, simulation_id):
    '''Accept form data, and save chip reader to database'''
    # Ensure request method is POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    # Instantiate RFIDForm modelform and supply attributes
    form = RFIDForm(request.POST)
    new_reader = form.save(commit=False)
    # Update fields
    simulation_obj = Simulation.objects.get(pk=simulation_id)
    new_reader.simulation = simulation_obj
    RANGE_LOOKUP = {'Low Frequency': 2, 'High Frequency': 10, 'Ultra High Frequency': 100}
    new_reader.chip_range = RANGE_LOOKUP[new_reader.chip_class] 
    y = new_reader.location.y
    x = new_reader.location.x
    new_reader.latitude = y
    new_reader.longitude = x
    # Save the form
    new_reader.save()
    # Get geometry of new place
    center = geos.Point(x, y)
    # Create buffer of new place
    buffer_geom = center.buffer(new_reader.chip_range)
    # Save buffer to buffers db table
    rfid_obj = RFIDReader.objects.get(pk=new_reader.id)
    new_buffer = ChipBuffer(simulation=simulation_obj, reader=rfid_obj, buffer=buffer_geom)
    new_buffer.save()
    # Add point and buffer to the map
    return JsonResponse({'success': 'true'})


def run_simulation(request, sim_id):
    '''Run the simulation'''
    rfid_route_intersect(sim_id)# Intersect function
    sim = Simulation.objects.get(pk=sim_id)
    # Mark the simulation run and save
    sim.run = True
    sim.save()
    # Return QuerySet as JSON object for the results table
    results = sim.readers.values("id", "chip_class", "chip_range", "route_count").order_by("id")
    return JsonResponse({'results': list(results)})


def get_readers(request, sim_id):
    '''Get simulation's readers, and return as json'''
    readers = Simulation.objects.get(pk=sim_id).readers.all()
    readers_json = serialize('geojson', readers)
    return HttpResponse(readers_json, content_type='json')


def get_buffers(request, sim_id):
    '''Get simulation's buffers, and return as json'''
    buffers = Simulation.objects.get(pk=sim_id).buffers.all()
    readers_json = serialize('geojson', buffers)
    return HttpResponse(readers_json, content_type='json')


def get_routes(request, sim_id):
    '''Get simulation's routes, and return as json'''
    routes = Simulation.objects.get(pk=sim_id).routes.all()
    routes_json = serialize('geojson', routes)
    return HttpResponse(routes_json, content_type='json')


@csrf_exempt
@login_required
def generate_route(request):
    '''Save route to database'''
    # Ensure request method is POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    sim_id = data.get("sim_id")
    sim = Simulation.objects.get(pk=sim_id)
    geom = data.get("geom")
    # Create GEOS linestring object, and transform to EPSG3857 CRS
    geom = LineString(geom['coordinates'], srid=4326)
    ct = CoordTransform(SpatialReference(4326), SpatialReference(3857))
    geom.transform(ct)
    # Save route to db
    new_route = Route(simulation=sim, trip_geometry=geom, trip_distance=0, trip_time=0) 
    new_route.save()
    return HttpResponse("Route created successfully.")


def rfid_route_intersect(sim_id):
    '''Get a count of routes intersecting each buffer, and save to corresponding chip reader'''
    buffers = Simulation.objects.get(pk=sim_id).buffers.all()
    # Loop buffers
    for buffer in buffers:
        # Spatial lookup
        buffer_geom = buffer.buffer
        routes = Simulation.objects.get(pk=sim_id).routes.filter(trip_geometry__intersects=buffer_geom)
        # Get count
        route_count = routes.count()
        reader = buffer.reader
        reader.route_count = route_count
        reader.save()
    return


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "rfid_sim/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "rfid_sim/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "rfid_sim/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "rfid_sim/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "rfid_sim/register.html")
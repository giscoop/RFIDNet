from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("simulations", views.my_simulations, name="my_sims"),
    path("simulations/<int:sim_id>", views.view_simulation, name="simulation"),

    # API Routes
    
    path("simulations/<int:sim_id>/run", views.run_simulation, name="run_simulation"),
    path("simulations/new", views.create_simulation, name="new_sim"),
    path("rfidreaders/new/<int:simulation_id>", views.create_chip_reader, name="new_reader"),
    path("rfidreaders/<int:sim_id>", views.get_readers, name="get_readers"),
    path("rfidbuffers/<int:sim_id>", views.get_buffers, name="get_buffers"),
    path("routes/new", views.generate_route, name="new_route"),
    path("routes/<int:sim_id>", views.get_routes, name="get_routes"),
]
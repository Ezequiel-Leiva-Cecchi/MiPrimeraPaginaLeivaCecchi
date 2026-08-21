from datetime import date

from django.db import migrations


PELICULAS = (
    ("Jurassic Park", date(1993, 6, 11), "Un parque con dinosaurios clonados se descontrola y convierte una visita extraordinaria en una lucha por sobrevivir.", ("Steven", "Spielberg"), ("Ciencia Ficción", "Aventura"), "posters/Jurassic_Park_1993_768_x_1152_by_John_Guydo.jpeg"),
    ("Salvar al Soldado Ryan", date(1998, 7, 24), "Durante la Segunda Guerra Mundial, un grupo de soldados atraviesa territorio enemigo para encontrar a un paracaidista desaparecido.", ("Steven", "Spielberg"), ("Bélica", "Drama"), "posters/salvar_al_sodadoRyan.jpeg"),
    ("Inception", date(2010, 7, 16), "Un especialista en infiltrarse en los sueños recibe la misión imposible de implantar una idea en la mente de su objetivo.", ("Christopher", "Nolan"), ("Ciencia Ficción", "Acción"), "posters/Inception_2010.jpeg"),
    ("Dunkerque", date(2017, 7, 21), "Miles de soldados aliados quedan atrapados en una playa mientras una evacuación desesperada se organiza por tierra, mar y aire.", ("Christopher", "Nolan"), ("Bélica", "Drama"), "posters/Dunkirk.jpeg"),
    ("Pulp Fiction", date(1994, 10, 14), "Las vidas de criminales, boxeadores y personajes impredecibles se cruzan en una historia contada fuera del orden convencional.", ("Quentin", "Tarantino"), ("Crimen", "Drama"), "posters/pulp_fiction.jpeg"),
    ("Kill Bill: Volumen 1", date(2003, 10, 10), "Una antigua asesina despierta después de años en coma y emprende una implacable búsqueda de venganza.", ("Quentin", "Tarantino"), ("Acción", "Suspenso"), "posters/Kill_Bill__Volume_1_by_Paul_Mann.jpeg"),
)


def cargar_catalogo(apps, schema_editor):
    Director = apps.get_model("peliculas_app", "Director")
    Genero = apps.get_model("peliculas_app", "Genero")
    Pelicula = apps.get_model("peliculas_app", "Pelicula")
    for titulo, estreno, resumen, datos_director, nombres_generos, imagen in PELICULAS:
        director, _ = Director.objects.get_or_create(nombre=datos_director[0], apellido=datos_director[1])
        pelicula, _ = Pelicula.objects.update_or_create(
            titulo=titulo,
            defaults={"fecha_lanzamiento": estreno, "mini_resumen": resumen, "director": director, "imagen": imagen},
        )
        pelicula.generos.set([Genero.objects.get_or_create(nombre=nombre)[0] for nombre in nombres_generos])


class Migration(migrations.Migration):
    dependencies = [("peliculas_app", "0005_alter_pelicula_options_enlista_resena")]
    operations = [migrations.RunPython(cargar_catalogo, migrations.RunPython.noop)]

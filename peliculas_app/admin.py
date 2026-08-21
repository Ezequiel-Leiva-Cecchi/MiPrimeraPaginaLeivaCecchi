from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Director, EnLista, Genero, Pelicula, Resena

@admin.register(Director)
class DirectorAdmin(ImportExportModelAdmin):
    search_fields = ['nombre', 'apellido']
    list_display = ['nombre', 'apellido']

@admin.register(Genero)
class GeneroAdmin(ImportExportModelAdmin):
    search_fields = ['nombre']
    list_display = ['nombre']

@admin.register(Pelicula)
class PeliculaAdmin(ImportExportModelAdmin):
    search_fields = ['titulo']
    list_display = ['titulo', 'fecha_lanzamiento', 'director']
    list_filter = ['director', 'generos', 'fecha_lanzamiento']

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['pelicula', 'usuario', 'puntuacion', 'actualizada']
    list_filter = ['puntuacion']

@admin.register(EnLista)
class EnListaAdmin(admin.ModelAdmin):
    list_display = ['pelicula', 'usuario', 'agregada']

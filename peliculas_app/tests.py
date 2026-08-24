from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Director, EnLista, Genero, Pelicula, Resena


class CineVaultTests(TestCase):
    def setUp(self):
        self.director = Director.objects.create(nombre="Christopher", apellido="Nolan")
        self.genero = Genero.objects.create(nombre="Ciencia ficción")
        self.pelicula = Pelicula.objects.create(
            titulo="Inception",
            fecha_lanzamiento=date(2010, 7, 16),
            mini_resumen="Un ladrón entra en los sueños.",
            director=self.director,
        )
        self.pelicula.generos.add(self.genero)
        self.user = User.objects.create_user("cinefilo", password="una-clave-segura")

    def test_catalogo_y_detalle_son_publicos(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)
        self.assertContains(
            self.client.get(reverse("detalle_pelicula", args=[self.pelicula.pk])),
            "Inception",
        )

    def test_busqueda_por_director_y_genero(self):
        response = self.client.get(
            reverse("buscar_pelicula"), {"q": "Nolan", "genero": self.genero.pk}
        )
        self.assertContains(response, "Inception")

    def test_catalogo_pagina_resultados_y_conserva_filtros(self):
        for numero in range(13):
            pelicula = Pelicula.objects.create(
                titulo=f"Pelicula {numero:02d}",
                fecha_lanzamiento=date(2000 + numero, 1, 1),
                mini_resumen="Película de prueba.",
                director=self.director,
            )
            pelicula.generos.add(self.genero)

        response = self.client.get(
            reverse("buscar_pelicula"), {"genero": self.genero.pk, "page": 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(response.context["total_resultados"], 14)
        self.assertContains(response, f"genero={self.genero.pk}")

    def test_lista_personal_agrega_y_elimina_sin_duplicar(self):
        self.client.force_login(self.user)
        url = reverse("alternar_lista", args=[self.pelicula.pk])
        self.client.post(url)
        self.assertTrue(
            EnLista.objects.filter(usuario=self.user, pelicula=self.pelicula).exists()
        )
        self.client.post(url)
        self.assertFalse(
            EnLista.objects.filter(usuario=self.user, pelicula=self.pelicula).exists()
        )

    def test_lista_personal_rechaza_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("alternar_lista", args=[self.pelicula.pk]))
        self.assertEqual(response.status_code, 405)

    def test_resena_se_actualiza_en_lugar_de_duplicarse(self):
        self.client.force_login(self.user)
        url = reverse("guardar_resena", args=[self.pelicula.pk])
        self.client.post(url, {"puntuacion": 4, "comentario": "Muy buena"})
        self.client.post(url, {"puntuacion": 5, "comentario": "Excelente"})
        self.assertEqual(Resena.objects.count(), 1)
        self.assertEqual(Resena.objects.get().puntuacion, 5)

    def test_resena_rechaza_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("guardar_resena", args=[self.pelicula.pk]))
        self.assertEqual(response.status_code, 405)

    def test_detalle_muestra_promedio_de_resenas(self):
        Resena.objects.create(
            usuario=self.user,
            pelicula=self.pelicula,
            puntuacion=4,
            comentario="Muy buena",
        )
        response = self.client.get(reverse("detalle_pelicula", args=[self.pelicula.pk]))
        self.assertContains(response, "4,0/5")

    def test_usuario_comun_no_puede_administrar_peliculas(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("pelicula_editar", args=[self.pelicula.pk]))
        self.assertEqual(response.status_code, 403)

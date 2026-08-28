from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Mensaje


class MensajesTests(TestCase):
    def setUp(self):
        self.emisor = User.objects.create_user("emisor", password="clave-segura")
        self.receptor = User.objects.create_user("receptor", password="clave-segura")
        self.otro = User.objects.create_user("otro", password="clave-segura")
        self.mensaje = Mensaje.objects.create(
            emisor=self.emisor,
            receptor=self.receptor,
            contenido="Tenés que ver esta película.",
        )

    def test_bandeja_requiere_login(self):
        response = self.client.get(reverse("bandeja_entrada"))
        self.assertEqual(response.status_code, 302)

    def test_bandeja_muestra_solo_mensajes_del_usuario(self):
        Mensaje.objects.create(
            emisor=self.emisor,
            receptor=self.otro,
            contenido="Mensaje para otra persona.",
        )
        self.client.force_login(self.receptor)
        response = self.client.get(reverse("bandeja_entrada"))
        self.assertContains(response, "Tenés que ver esta película.")
        self.assertNotContains(response, "Mensaje para otra persona.")

    def test_abrir_mensaje_lo_marca_como_leido(self):
        self.client.force_login(self.receptor)
        response = self.client.get(reverse("detalle_mensaje", args=[self.mensaje.pk]))
        self.assertEqual(response.status_code, 200)
        self.mensaje.refresh_from_db()
        self.assertTrue(self.mensaje.leido)

    def test_otro_usuario_no_puede_abrir_mensaje(self):
        self.client.force_login(self.otro)
        response = self.client.get(reverse("detalle_mensaje", args=[self.mensaje.pk]))
        self.assertEqual(response.status_code, 404)

    def test_no_se_puede_enviar_mensaje_a_uno_mismo(self):
        self.client.force_login(self.emisor)
        response = self.client.post(
            reverse("enviar_mensaje"),
            {"receptor": self.emisor.pk, "contenido": "Mensaje propio"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Mensaje.objects.filter(contenido="Mensaje propio").exists())

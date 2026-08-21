from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Director(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Genero(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    titulo = models.CharField(max_length=100)
    fecha_lanzamiento = models.DateField()
    mini_resumen = models.TextField()
    director = models.ForeignKey(Director, on_delete=models.CASCADE)
    generos = models.ManyToManyField(Genero)
    imagen = models.ImageField(upload_to='posters/', blank=True, null=True)

    class Meta:
        ordering = ("-fecha_lanzamiento", "titulo")

    def clean(self):
        # Validar que el título no esté vacío
        if not self.titulo.strip():
            raise ValidationError({'titulo': 'El título no puede estar vacío.'})
        # Validar que el mini_resumen no esté vacío
        if not self.mini_resumen.strip():
            raise ValidationError({'mini_resumen': 'El resumen no puede estar vacío.'})
        # Validar que la fecha de lanzamiento no sea futura
        if self.fecha_lanzamiento > timezone.now().date():
            raise ValidationError({'fecha_lanzamiento': 'La fecha de lanzamiento no puede ser futura.'})

    def __str__(self):
        return self.titulo

    @property
    def anio(self):
        return self.fecha_lanzamiento.year


class Resena(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resenas")
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name="resenas")
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(max_length=800, blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "pelicula"), name="resena_unica_por_usuario"
            )
        ]
        ordering = ("-actualizada",)

    def __str__(self):
        return f"{self.pelicula} · {self.puntuacion}/5"


class EnLista(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lista_cine")
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name="en_listas")
    agregada = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("usuario", "pelicula"), name="pelicula_unica_en_lista"
            )
        ]
        ordering = ("-agregada",)

    def __str__(self):
        return f"{self.usuario} → {self.pelicula}"

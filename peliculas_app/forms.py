from django.forms import ModelForm
from .models import Director, Genero, Pelicula
from django import forms
from django.utils import timezone


class DirectorForm(ModelForm):
    class Meta:
        model = Director
        fields = "__all__"


class GeneroForm(ModelForm):
    class Meta:
        model = Genero
        fields = "__all__"


class PeliculaForm(ModelForm):
    class Meta:
        model = Pelicula
        fields = "__all__"

    def clean_titulo(self):
        titulo = self.cleaned_data.get("titulo", "").strip()
        if not titulo:
            raise forms.ValidationError("El título no puede estar vacío.")
        return titulo

    def clean_mini_resumen(self):
        mini_resumen = self.cleaned_data.get("mini_resumen", "").strip()
        if not mini_resumen:
            raise forms.ValidationError("El resumen no puede estar vacío.")
        return mini_resumen

    def clean_fecha_lanzamiento(self):
        fecha = self.cleaned_data.get("fecha_lanzamiento")
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de lanzamiento no puede ser futura.")
        return fecha


class BusquedaForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Título, director o palabra clave", "autocomplete": "off"}
        ),
    )
    genero = forms.ModelChoiceField(
        label="Género",
        queryset=Genero.objects.all().order_by("nombre"),
        required=False,
        empty_label="Todos los géneros",
    )
    orden = forms.ChoiceField(
        label="Ordenar",
        required=False,
        choices=(
            ("recientes", "Más recientes"),
            ("valoradas", "Mejor valoradas"),
            ("populares", "Más guardadas"),
            ("titulo", "A–Z"),
            ("clasicos", "Más antiguas"),
        ),
    )


class ResenaForm(forms.Form):
    puntuacion = forms.TypedChoiceField(
        label="Tu puntuación",
        coerce=int,
        choices=(
            (5, "5 · Excelente"),
            (4, "4 · Muy buena"),
            (3, "3 · Buena"),
            (2, "2 · Regular"),
            (1, "1 · Mala"),
        ),
    )
    comentario = forms.CharField(
        label="Reseña",
        required=False,
        max_length=800,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "¿Qué te pareció? Contá qué te dejó la película.",
            }
        ),
    )

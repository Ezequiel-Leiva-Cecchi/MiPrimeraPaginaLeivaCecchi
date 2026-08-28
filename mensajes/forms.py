from django import forms
from django.contrib.auth.models import User
from .models import Mensaje


class MensajeForm(forms.ModelForm):
    receptor = forms.ModelChoiceField(
        label="Para",
        queryset=User.objects.none(),
        empty_label="Elegí una persona",
    )

    class Meta:
        model = Mensaje
        fields = ["receptor", "contenido"]
        labels = {"contenido": "Mensaje"}
        widgets = {
            "contenido": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Escribí tu mensaje...",
                    "maxlength": 2000,
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        usuarios = User.objects.filter(is_active=True).order_by("username")
        if user and user.is_authenticated:
            usuarios = usuarios.exclude(pk=user.pk)
        self.fields["receptor"].queryset = usuarios

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.generic import DetailView

from .forms import MensajeForm
from .models import Mensaje


@login_required
def bandeja_entrada(request):
    mensajes_recibidos = Mensaje.objects.filter(receptor=request.user).select_related("emisor").order_by("-fecha_envio")
    return render(
        request,
        "mensajes/bandeja_entrada.html",
        {
            "mensajes": mensajes_recibidos,
            "sin_leer": mensajes_recibidos.filter(leido=False).count(),
        },
    )


@login_required
def enviar_mensaje(request):
    destinatario = None
    destinatario_id = request.GET.get("para")
    if destinatario_id:
        destinatario = User.objects.filter(pk=destinatario_id, is_active=True).exclude(pk=request.user.pk).first()

    if request.method == "POST":
        form = MensajeForm(request.POST, user=request.user)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.emisor = request.user
            mensaje.save()
            messages.success(request, "Mensaje enviado.")
            return redirect("bandeja_entrada")
    else:
        form = MensajeForm(user=request.user, initial={"receptor": destinatario})

    return render(request, "mensajes/enviar_mensaje.html", {"form": form})


class MensajeDetalleView(LoginRequiredMixin, DetailView):
    model = Mensaje
    template_name = "mensajes/detalle_mensaje.html"
    context_object_name = "mensaje"

    def get_queryset(self):
        return Mensaje.objects.filter(receptor=self.request.user).select_related("emisor")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.leido:
            obj.leido = True
            obj.save(update_fields=["leido"])
        return obj

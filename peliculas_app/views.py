from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg, Count, Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .forms import BusquedaForm, ResenaForm
from .models import EnLista, Pelicula, Resena
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


def _peliculas_con_metricas():
    return (
        Pelicula.objects.select_related("director")
        .prefetch_related("generos")
        .annotate(
            puntuacion_media=Avg("resenas__puntuacion"),
            total_resenas=Count("resenas", distinct=True),
            total_guardadas=Count("en_listas", distinct=True),
        )
    )


def index(request):
    catalogo = _peliculas_con_metricas()
    destacada = catalogo.order_by(
        "-puntuacion_media", "-total_resenas", "-total_guardadas", "-fecha_lanzamiento"
    ).first()
    peliculas = list(catalogo.order_by("-fecha_lanzamiento", "titulo")[:8])
    mejor_valoradas = catalogo.filter(total_resenas__gt=0).order_by(
        "-puntuacion_media", "-total_resenas", "titulo"
    )[:4]

    generos = {}
    for pelicula in peliculas:
        for genero in pelicula.generos.all():
            generos[genero.nombre] = genero

    return render(
        request,
        "peliculas_app/index.html",
        {
            "peliculas": peliculas,
            "destacada": destacada,
            "mejor_valoradas": mejor_valoradas,
            "generos_destacados": list(generos.values())[:6],
            "total_peliculas": Pelicula.objects.count(),
            "total_resenas_global": Resena.objects.count(),
        },
    )


def buscar_pelicula(request):
    resultados = _peliculas_con_metricas()
    form = BusquedaForm(request.GET or None)

    if form.is_valid():
        q = form.cleaned_data["q"]
        genero = form.cleaned_data["genero"]
        orden = form.cleaned_data["orden"] or "recientes"

        if q:
            resultados = resultados.filter(
                Q(titulo__icontains=q)
                | Q(mini_resumen__icontains=q)
                | Q(director__nombre__icontains=q)
                | Q(director__apellido__icontains=q)
            )
        if genero:
            resultados = resultados.filter(generos=genero)

        campos_orden = {
            "titulo": ("titulo",),
            "clasicos": ("fecha_lanzamiento", "titulo"),
            "valoradas": ("-puntuacion_media", "-total_resenas", "titulo"),
            "populares": ("-total_guardadas", "-puntuacion_media", "titulo"),
            "recientes": ("-fecha_lanzamiento", "titulo"),
        }
        resultados = resultados.order_by(*campos_orden.get(orden, campos_orden["recientes"])).distinct()

    paginator = Paginator(resultados, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "peliculas_app/buscar.html",
        {
            "form": form,
            "resultados": page_obj.object_list,
            "page_obj": page_obj,
            "total_resultados": paginator.count,
            "querystring": query_params.urlencode(),
        },
    )


def detalle_pelicula(request, pelicula_id):
    pelicula = get_object_or_404(
        _peliculas_con_metricas().prefetch_related("resenas__usuario"), pk=pelicula_id
    )
    en_lista = request.user.is_authenticated and EnLista.objects.filter(
        usuario=request.user, pelicula=pelicula
    ).exists()
    resena_usuario = None
    if request.user.is_authenticated:
        resena_usuario = Resena.objects.filter(
            usuario=request.user, pelicula=pelicula
        ).first()

    relacionados = (
        _peliculas_con_metricas()
        .filter(generos__in=pelicula.generos.all())
        .exclude(pk=pelicula.pk)
        .distinct()[:4]
    )

    return render(
        request,
        "peliculas_app/detalle_pelicula.html",
        {
            "pelicula": pelicula,
            "en_lista": en_lista,
            "resena_usuario": resena_usuario,
            "form_resena": ResenaForm(
                initial={
                    "puntuacion": getattr(resena_usuario, "puntuacion", 5),
                    "comentario": getattr(resena_usuario, "comentario", ""),
                }
            ),
            "relacionados": relacionados,
        },
    )


def about(request):
    return render(request, "peliculas_app/about.html")


@login_required
@require_POST
def alternar_lista(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    item, creado = EnLista.objects.get_or_create(usuario=request.user, pelicula=pelicula)
    if not creado:
        item.delete()
    messages.success(
        request,
        "Película agregada a tu lista." if creado else "Película eliminada de tu lista.",
    )
    siguiente = request.POST.get("next")
    if siguiente:
        return redirect(siguiente)
    return redirect("detalle_pelicula", pelicula_id=pelicula_id)


@login_required
@require_POST
def guardar_resena(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id)
    form = ResenaForm(request.POST)
    if form.is_valid():
        Resena.objects.update_or_create(
            usuario=request.user, pelicula=pelicula, defaults=form.cleaned_data
        )
        messages.success(request, "Tu reseña quedó guardada.")
    else:
        messages.error(request, "Revisá la puntuación o el comentario antes de guardar.")
    return redirect("detalle_pelicula", pelicula_id=pelicula_id)


@login_required
def mi_lista(request):
    items = (
        EnLista.objects.filter(usuario=request.user)
        .select_related("pelicula", "pelicula__director")
        .prefetch_related("pelicula__generos")
        .order_by("-id")
    )
    return render(request, "peliculas_app/mi_lista.html", {"items": items})


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class PeliculaCreateView(StaffRequiredMixin, CreateView):
    model = Pelicula
    fields = ["titulo", "fecha_lanzamiento", "mini_resumen", "director", "generos", "imagen"]
    template_name = "peliculas_app/pelicula_form.html"
    success_url = reverse_lazy("index")


class PeliculaUpdateView(StaffRequiredMixin, UpdateView):
    model = Pelicula
    fields = ["titulo", "fecha_lanzamiento", "mini_resumen", "director", "generos", "imagen"]
    template_name = "peliculas_app/pelicula_form.html"
    success_url = reverse_lazy("index")


class PeliculaDeleteView(StaffRequiredMixin, DeleteView):
    model = Pelicula
    template_name = "peliculas_app/pelicula_confirm_delete.html"
    success_url = reverse_lazy("index")

from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy

from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, UpdateView, DeleteView

from modulo.clases.select2 import Select2JSONResponseMixin
from modulo.clases.table_lista import TableListView
from modulo.forms import TestDataForm
from modulo.models import TestData


# Create your views here.

class SuccessView(View):

    def get(self, request, pk):
        return JsonResponse({
            "success": True,
            "mensaje": "Guardado Correctamente",
            "pk": pk
        })


class HomeView(TemplateView):
    template_name = "modulo/test/vista.html"


class ListaView(ListView):
    model = TestData
    template_name = "modulo/test/lista.html"
    paginate_by = 5
    ordering = ['id']

    def get_queryset(self):
        query = super(ListaView, self).get_queryset()
        search = self.request.GET.get("search")
        pagination = self.request.GET.get("pagination")
        if pagination:
            print(pagination)
            self.paginate_by = int(pagination)
        if search:
            query = query.filter(
                Q(name__icontains=search)
            )
        return query


class TableListaView(TableListView):
    model = TestData
    template_name = "modulo/test/table_lista.html"
    paginate_by = 10
    ordering = ['id']
    headers = ['Nombre', "Activo"]

    def get_queryset(self):
        query = super(TableListView, self).get_queryset()
        search = self.request.GET.get("search")
        if search:
            query = query.filter(
                Q(name__icontains=search)
            )
        return query


class CrearView(CreateView):
    model = TestData
    form_class = TestDataForm
    template_name = "modulo/formulario/formulario.html"


class EditarView(UpdateView):
    model = TestData
    form_class = TestDataForm
    template_name = "modulo/formulario/formulario.html"


class EliminarView(DeleteView):
    model = TestData
    template_name = "modulo/formulario/eliminar.html"
    success_url = reverse_lazy('modulo:success', kwargs={'pk': 0})


class ComboView(Select2JSONResponseMixin, TemplateView):
    model = TestData
    filters = ['name']

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

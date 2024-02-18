from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse


class Select2JSONResponseMixin:
    model = None
    request = None
    queryset = None
    filters = []
    filtro = {}  # {'persona__id': 1}
    order_by = None  # lista de orden
    slug_pk = None  # si no es id el atributo de retorno (pk)
    slug_text = None

    """
    A mixin that can be used to render a JSON response.
    """

    def get_queryset(self):
        # si la variable queryset es diferente de None la consulta puede ser modificada
        return self.queryset or self.model.objects.all()

    def get_filtro(self):
        # El método puede ser modificado para personalizar el filtro
        return self.filtro.copy()

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """

        search = self.request.GET.get('search', "")
        page = self.request.GET.get('page', 1)
        objeto = self.get_queryset()
        objeto = objeto.order_by(f"{','.join(self.order_by) if self.order_by else '-id'}")
        self.filtro = self.get_filtro()
        if self.filtro:
            f = [f"{key}={self.filtro[key]} " for key in self.filtro.keys()]
            f = ', '.join(f)
            f = f"objeto.filter({f}).order_by(f'{','.join(self.order_by) if self.order_by else '-id'}')"
            objeto = eval(f)
        if search is not None:
            filtro = [f"Q({valor}__icontains=search) " for valor in self.filters]
            objeto = objeto.filter(
                eval("| ".join(filtro))
            ).order_by(f"{','.join(self.order_by) if self.order_by else '-id'}")

        paginator = Paginator(objeto, 6)
        obj = paginator.get_page(page)
        lista = list()
        for object in obj:
            dict = {
                "id": object.id if self.slug_pk is None else eval(f"object.{self.slug_pk}"),
                "text": object.__str__() if not self.slug_text else eval(f"object.{self.slug_text}")
            }
            lista.append(dict)
        context['results'] = lista
        context['pagination'] = {"more": obj.has_next()}
        object = {
            "results": lista,
            "pagination": {"more": obj.has_next()}
        }
        return JsonResponse(object)

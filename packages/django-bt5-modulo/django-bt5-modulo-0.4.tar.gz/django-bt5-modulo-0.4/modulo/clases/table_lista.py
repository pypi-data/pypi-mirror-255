from django.views.generic import ListView


class TableListView(ListView):
    headers = []

    def get_headers(self):
        return self.headers

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['headers'] = self.headers
        return ctx

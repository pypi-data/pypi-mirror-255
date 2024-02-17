django-lazycrud
===============

A little Django app to reduce boilerplate code at a minimum when you write class based views in a typical CRUD scenario.

Django compatibility
--------------------

The app is tested on Django 1.8 and 1.11.

Dependencies:
-------------

The app depends on `django-crispy-forms <http://django-crispy-forms.readthedocs.io/en/latest/>`_ to generate forms and includes a static version of
`Datatables <https://datatables.net/>`_ and `Bootstrap Datepicker <https://bootstrap-datepicker.readthedocs.io/en/latest/>`_ to provide
client side enhancements to tables and forms.

Install:
--------

::

    pip install django-lazycrud

Then add `lazycrud` and `crispy_forms` to your `INSTALLED_APPS` in Django settings.

Example:
---------

Define your CRUD views with few lines of Python code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No need to write any html code, let lazycrud handle all the templates for you.

::

    from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
    from django.core.urlresolvers import reverse_lazy

    from .models import Model

    class ModelListView(ListView):
        model = Model
        template_name = 'lazycrud/object_list.html'
        page_title = 'My Model list'
        fields = [ 'model_field1', 'model_field2', ]
        create_url = reverse_lazy('yourapp:model_create')
        create_label = 'Create new Model'

    class ModelDetailView(DetailView):
        model = Model
        template_name = 'lazycrud/object_detail.html'
        fields = [ 'model_field1', 'model_field2', 'model_field3', ]
        update_url = 'yourapp:model_update'
        delete_url = 'yourapp:model_delete'

    class ModelCreateView(CreateView):
        model = Model
        template_name = 'lazycrud/object_form.html'
        form_title = 'Create new Model'
        fields = [ 'model_field1', 'model_field2', 'model_field3', ]

    class ModelUpdateView(UpdateView):
        model = Model
        template_name = 'lazycrud/object_form.html'
        form_title = 'Edit Model'
        fields = ModelCreateView.fields

    class ModelDeleteView(DeleteView):
        model = Model
        template_name = 'lazycrud/object_confirm_delete.html'
        success_url = reverse_lazy('yourapp:model_list')

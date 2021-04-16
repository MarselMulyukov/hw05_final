#  импортируем CreateView, чтобы создать ему наследника
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm

#  функция reverse_lazy позволяет получить URL по параметру "name" функции
#  path()
#  берём, тоже пригодится


#  импортируем класс формы, чтобы сослаться на неё во view-классе


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("signup")  # где signup — это параметр "name"
    # в path()
    template_name = "signup.html"

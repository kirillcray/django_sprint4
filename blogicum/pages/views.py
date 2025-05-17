from django.views.generic import TemplateView

# Create your views here.
from django.shortcuts import render


class AboutView(TemplateView):
    """Отображает страницу 'О нас'."""

    template_name = "pages/about.html"


class RulesView(TemplateView):
    """Отображает страницу 'Правила'."""

    template_name = "pages/rules.html"


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем.
    return render(request, "pages/404.html", status=404)


def server_error(request):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 500 мы не станем.
    return render(request, "pages/500.html", status=500)


def permission_denied(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 403 мы не станем.
    return render(request, "pages/403csrf.html", status=403)

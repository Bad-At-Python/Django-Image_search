from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from .models import VerifiedUser


def login(request, extra_context):

    class MyLoginView(LoginView):
        template_name = "users/login.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update({"extra_context": extra_context})
            return context

    return MyLoginView.as_view()(request)


def register(request):
    # Use this url for both submitting and processing
    if request.method == "POST":
        # Create a populated form with POST data
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            # Create new user in db
            user_form = user_form.save()
            VerifiedUser.objects.create(user=user_form, verified=False)

            return HttpResponseRedirect(reverse("search"))
    else:
        user_form = UserCreationForm()
    return render(request, "users/register.html", {"form": user_form})

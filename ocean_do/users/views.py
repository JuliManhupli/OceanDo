from django.shortcuts import render


def profile_view(request):
    return render(request, "users/profile.html")


def edit_profile_view(request):
    return render(request, "users/edit-profile.html")

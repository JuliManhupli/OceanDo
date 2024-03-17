from django.shortcuts import render


def main(request):
    return render(request, "ocean_do/index.html")



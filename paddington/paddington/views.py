from django.shortcuts import redirect


def redirect_to_my(request):
    """
    Redirect to my.mebaha.com for now
    """
    return redirect("http://store.{}".format(request.META["HTTP_HOST"]))

def select_domain(request):
    print(request.get_host())
    return {"is_weni": 'localhost' in request.get_host()}

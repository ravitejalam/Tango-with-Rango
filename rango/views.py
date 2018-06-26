from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response,render
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm,PageForm
from rango.forms import UserForm, UserProfileForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required


def index(request):
    # context = RequestContext(request)
    # context_dict = {'boldmessage': "I am bold font from the context"}
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,'pages':page_list}
    for category in category_list:
        category.url = category.name.replace(' ','-')
    return render(request,'rango/index.html', context_dict)
    # return HttpResponse('Rango says Welcome! <a href="/rango/about">About</a>')
def about(request):
    context = RequestContext(request)
    return render(request,'rango/about.html', {}, context)

    # return HttpResponse('Rango Says:Here is the about page. <a href="/rango">Home</a>')
def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

# def add_page(request, category_name_slug):
#     context = RequestContext(request)
#     category_name = decode_url(category_name_slug)
#     if request.method == 'POST':
#         form = PageForm(request.POST)
#         if form.is_valid():
#             page = form.save(commit=False)
#             cat = Category.objects.get(name=category_name)
#             page.category = cat
#             page.views = 0
#             page.save()
#             return category(request, category_name_slug)
#         else:
#             print(form.errors)
#     else:
#         form = PageForm()
#     return render( 'rango/add_page.html',
#         {'category_name_slug': category_name_slug,
#         'category_name': category_name, 'form': form},
#         context)

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
            else:
                print(form.errors)
    context_dict = {
        'form': form,
        'category': category
    }
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                profile.save()
                registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,'rango/register.html',
        {'user_form': user_form,'profile_form': profile_form,'registered': registered})

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password = password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your Rango account is disabled.')
        else:
            print("Invalid login details were provided. So we can't log the user in")
            return HttpResponse('Invalid login details supplied.')

    else:
        return render(request,'rango/login.html', {}, context)

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))
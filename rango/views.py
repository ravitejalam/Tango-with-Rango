from django.template import RequestContext
from django.shortcuts import render_to_response,render,redirect
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm,PageForm
from rango.forms import UserForm, UserProfileForm
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

from rango.bing_search import run_query


def index(request):
    request.session.set_test_cookie()
    # context = RequestContext(request)
    # context_dict = {'boldmessage': "I am bold font from the context"}
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,'pages':page_list}
    for category in category_list:
        category.url = category.name.replace(' ','-')
    response = render(request, 'rango/index.html', context_dict)
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context=context_dict)
    return response
    # return HttpResponse('Rango says Welcome! <a href="/rango/about">About</a>')
def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    context = RequestContext(request)
    visit=int(request.COOKIES.get('visits','1'))
    return render(request,'rango/about.html', {'count':visit}, context)

    # return HttpResponse('Rango Says:Here is the about page. <a href="/rango">Home</a>')
def show_category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()
    if query:
        result_list = run_query(query)
        context_dict['result_list'] = result_list
        context_dict['query'] = query
    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    if not context_dict['query']:
        context_dict['query'] = category.name
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

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits

def search(request):
	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			result_list = run_query(query)
	return render(request, 'rango/search.html', {'result_list': result_list})

def register_profile(request):
    print("resister profile")

@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username=request.user)
    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None
    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('rango/profile.html', context_dict, context)

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)
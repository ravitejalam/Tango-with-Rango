from django.conf.urls import include, url
from rango import views
#urlpatterns = patterns('',url(r'^$', views.index, name='index'))
app_name = 'rango'
urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^about/$',views.about, name='about'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name = 'add_page'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.show_category, name='show_category'),
    url(r'^register/$',views.register,name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^restricted/', views.restricted, name='restricted'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^search/$',views.search, name='search'),
    url(r'^rango/add_profile/$',views.register_profile,name='UserProfileForm'),
    url(r'^rango/profile/$',views.profile,name='profile'),
    url(r'^goto/$', views.track_url, name='goto'),
]
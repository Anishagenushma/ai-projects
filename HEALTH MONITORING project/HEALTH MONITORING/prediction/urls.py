from django.urls import path
from . views import *

urlpatterns = [
    path('',index,name='index' ),
    path('about',about,name='about' ),
    path('predict',predict,name='predict' ),
    path('patient',Patient,name='patient' ),

]
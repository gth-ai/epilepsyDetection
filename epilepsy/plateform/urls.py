from django.urls import path
from . import views,preprocessing,prediction


urlpatterns = [

    path('login/',views.loginPage,name='login'),
    path('register/',views.registerPage,name='register'),
    path('customer_settings/',views.customer_settings,name='customer_settings'),
    path('deleteUser/<int:pk>/',views.deleteUser,name='deleteUser'),
    path('logout/',views.logoutUser,name='logout'),
    path('no_autorize/',views.no_authorize,name='no_authorize'),

    path('dashboard/',views.dashboard,name='dashboard'),
    path('dashboard_edf/',views.dashboard_edf,name='dashboard_edf'),
    path('dashboard_user/',views.dashboard_user,name='dashboard_user'),
    path('dashboard_login/',views.dashboard_login,name='dashboard_login'),
    path('make_customer/<int:pk>/<str:cat>/',views.make_customer,name='make_customer'),
    path('update_customer_status/<int:pk>/<str:cat>/',views.update_customer_status,name='update_customer_status'),

    path('',views.home,name='home'),
    path('confirm_mail/<str:mode>/',views.confirm_mail,name='confirm_mail'),
    path('message/<str:mode>/',views.message_ask_mode_admin,name='message_to_admin'),
    path('normal/',views.normal,name='normal'),
    path('normal_edf_list/<str:pk>/',views.edf_normal_list,name='normal_edf_list'),
    path('expert/',views.expert,name='expert'),
    path('expert_edf_list/<str:pk>/',views.edf_list,name='expert_edf_list'),
    path('delete_edf/<int:pk>/',views.delete_edf,name='delete_edf'),
    path('explore_edf/',views.explore_edf,name='explore_edf'),
    path('preprocessing_edf/<int:pk>/',preprocessing.preprocessing,name='preprocessing_edf'),
    path('missing_point_file/',preprocessing.missingPointFile,name='missing_point_file'),
    path('prediction_edf/<int:pk>/',prediction.make_prediction,name='prediction_edf'),
    path('normal/',views.normal,name='normal'),
    
]


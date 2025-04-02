from django.urls import path
from . import views
urlpatterns = [
    # Login
    path('signup/', views.signup,name="signup"),
    path('logout/', views.signout,name="logout"),
    path('signin/', views.signin,name="signin"),

    # Admin usuaris
    path('userList/', views.userList,name="userList"),
    path('userChangePriv/<int:user_id>/', views.userList,name="userChangePriv"),

    # Admin workers
    path('workerList/', views.workerList,name="workerList"),
    path('borrar_worker/<int:worker_id>/', views.borrar_worker, name='borrar_worker'),  # Vista para borrar una reserva
]

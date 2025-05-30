from django.urls import path
from . import views
urlpatterns = [
    # Login
    path('signup/', views.signup,name="signup"),
    path('logout/', views.signout,name="logout"),
    path('signin/', views.signin,name="signin"),

    # Admin usuaris
    path('editUser/', views.editUser,name="editUser"),
    path('userList/', views.userList,name="userList"),
    path('userChangePriv/<int:user_id>/', views.userList,name="userChangePriv"),

    # Admin workers
    path('workerList/', views.workerList,name="workerList"),
    path('borrar_worker/<int:worker_id>/', views.borrar_worker, name='borrar_worker'),  
    path('editWorker/', views.editar_worker,name="editWorker"),
    path('restore_worker/', views.restore_worker, name='restore_worker'), 
    path('createWorker/', views.crear_worker,name="createWorker"),
    path('importar-workers/', views.importar_workers,name="importar-workers"),
    path('forgot-username/', views.forgot_username, name='forgot_username'),
    path('recover-user/', views.recover_user, name='recover_user'),

    path('accounts/password/reset/', views.redirect_password_reset, name='password_reset_redirect'),

]

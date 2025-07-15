from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path("", views.check_in, name="check_in"),
    path("payment", views.payment_proof, name="payment_proof"),
    path("Paymentproof", views.payment_redirect, name="payment_redirect"),
    path("accept/<int:proof_id>/", views.accept_payment, name="accept_payment"),
    path("cancel/<int:proof_id>/", views.cancel_payment, name="cancel_payment"),

    path("dashboard", views.dashboard, name="dashboard"),
    path("schedule", views.schedule, name="schedule"),
    path("approving", views.payment, name="approving"),
    path("refund", views.event_status, name="refund"),
    path("admin_setting", views.admin_setting, name="admin_setting" ),
 


    path("user_dashboard", views.user_dashboard, name="user_dashboard"),
    path("delete_book/<int:id>/", views.delete_book, name="delete_book"),
    path("cancel_book/<int:id>/", views.cancel_book, name="cancel_book"),
    path("refund/<int:id>/", views.refund_complete, name="refund_complete"),
    

    path("policies", views.policies, name="policies")

]
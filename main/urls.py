from django.urls import path
from . import views

app_name = "main"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.make_order, name="make_order"),
    path("total_orders", views.total_orders, name="total_orders"),
    path("total_orders/month_sales", views.month_sales, name="month_sales"),
    path("users/", views.users, name="users"),
    path("users/all_orders", views.all_orders, name="all_orders"),
    path("users/all_coming_orders", views.all_coming_orders, name="all_coming_orders"),
    path("users/<int:user_id>", views.user, name="user"),    
    path("order_info/<int:order_id>", views.order_info, name="order_info"),
    path("order_info/<int:order_id>/add_items", views.add_items, name="add_items"),
    path("edit_order/<int:order_id>", views.edit_order, name="edit_order"),
    path("change_rest", views.change_rest, name="change_rest"),
    path("put_rest", views.put_rest, name="put_rest"),
    path("delete_order/<int:order_id>", views.delete_order, name="delete_order"),
    path("delete_order_item/<int:order_item_id>", views.delete_order_item, name="delete_order_item"),
    path("change_rank/<int:order_id>", views.change_rank, name="change_rank"),
    path("order_error/<int:order_id>", views.order_error, name="order_error"),
    path("create_item", views.create_item, name="create_item"),
    path("coming_order", views.coming_order, name="coming_order"),
    path("coming_order/<int:order_id>", views.coming_order_info, name="coming_order_info"),
    path("coming_order/<int:order_id>/add_items", views.add_coming_items, name="add_coming_items"),
    path("coming_put_rest", views.coming_put_rest, name="coming_put_rest"),
    path("coming_change_rest", views.coming_change_rest, name="coming_change_rest"),

    path("edit_coming_item/<int:item_id>", views.edit_coming_item, name="edit_coming_item"),
    path("delete_coming_item/<int:item_id>", views.delete_coming_item, name="delete_coming_item"),
    path("delete_coming_order/<int:order_id>", views.delete_coming_order, name="delete_coming_order"),
    path("done_coming_order/<int:order_id>", views.done_coming_order, name="done_coming_order"),
    path("store_info/<int:store_id>", views.store_coming_info, name="store_coming_info"),
    path("supplier_info/<int:supplier_id>", views.supplier_coming_info, name="supplier_coming_info"),
    path("create_item", views.create_item, name="create_item"),
    path("create_category", views.create_category, name="create_category"),
    path("create_customer", views.create_customer, name="create_customer"),
    path("all_rest_orders", views.all_rest_orders, name="all_rest_orders"),
    path("all_rest_coming_orders", views.all_rest_coming_orders, name="all_rest_coming_orders"),

    path("items_view", views.items_view, name="items_view"),
    path("items_view/<int:item_id>", views.update_item, name="update_item"),
    ###################### api ######################         
    path("users_search/<str:text>", views.users_search, name="users_search"),
]
 
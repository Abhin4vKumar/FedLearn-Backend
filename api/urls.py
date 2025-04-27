from django.urls import path
# from .views import manipulate_string
from .views import add_dummy_node , remove_dummy_node , get_dummy_nodes , get_real_nodes , upload_file , upload_models

urlpatterns = [
    path('dummy/add/', add_dummy_node, name='add_dummy_node'),
    path('dummy/get/', get_dummy_nodes, name='get_dummy_node'),
    path('dummy/remove/', remove_dummy_node, name='remove_dummy_node'),
    path('real/get/', get_real_nodes, name='get_real_node'),
    path('upload/',upload_file, name="upload-file"),
    path('models/',upload_models, name="upload-models"),
]

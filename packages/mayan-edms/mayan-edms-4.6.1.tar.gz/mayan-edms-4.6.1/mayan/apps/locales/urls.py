from django.urls import re_path

from .views import UserLocaleProfileDetailView, UserLocaleProfileEditView

urlpatterns = [
    re_path(
        route=r'^user/(?P<user_id>\d+)/locale/$',
        name='user_locale_profile_detail',
        view=UserLocaleProfileDetailView.as_view()
    ),
    re_path(
        route=r'^user/(?P<user_id>\d+)/locale/edit/$',
        name='user_locale_profile_edit',
        view=UserLocaleProfileEditView.as_view()
    )
]

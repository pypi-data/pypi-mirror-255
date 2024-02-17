from django.views.generic import TemplateView
from . import views
from django.urls import path

app_name = 'django_cotton'

class NamedSlotInLoop(TemplateView):
    template_name = 'named_slot_in_loop.cotton.html'

    def get_context_data(self, **kwargs):
        return {
            'items': [
                {'name': 'Item 1'},
                {'name': 'Item 2'},
                {'name': 'Item 3'},
            ]
        }


urlpatterns = [
    path('parent', TemplateView.as_view(template_name='parent_test.cotton.html')),
    path('child', TemplateView.as_view(template_name='child_test.cotton.html')),
    path('self-closing', TemplateView.as_view(template_name='self_closing_test.cotton.html')),
    path('include', TemplateView.as_view(template_name='cotton_include.cotton.html')),
    path('playground', TemplateView.as_view(template_name='playground.cotton.html')),
    path('tag', TemplateView.as_view(template_name='tag.cotton.html')),
    path('named-slot-in-loop', NamedSlotInLoop.as_view()),
    path('test/compiled-cotton', views.compiled_cotton_test_view, name='test_compiled_cotton'),
    path('test/cotton', views.cotton_test_view, name='test_cotton'),
    path('test/native-extends', views.native_extends_test_view, name='test_native_extends'),
    path('test/native-include', views.native_include_test_view, name='test_native_include'),
    path('attribute-merging', views.attribute_merging_test_view, name='attribute_merging'),
    path('attribute-passing', views.attribute_passing_test_view, name='attribute_passing'),
]

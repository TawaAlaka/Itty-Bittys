from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login


class AnalystRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_analyst:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().dispatch(request, *args, **kwargs)

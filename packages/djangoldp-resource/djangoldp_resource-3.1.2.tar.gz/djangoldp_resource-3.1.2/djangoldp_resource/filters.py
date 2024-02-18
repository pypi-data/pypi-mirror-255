from django.db.models import Q
from djangoldp.filters import OwnerFilterBackend

class ResourceFilterBackend(OwnerFilterBackend):
    
    def filter_queryset(self, request, queryset, view):
        # Test if this not an anonymous user
        if request.user.is_authenticated:
            # Exclude all resources with privates circles not associated to this user
            return queryset.exclude(
                Q(circle__status__iexact='private') &
                ~Q(circle__members__user=request.user)
            )
        else :
            # Exclude all resources associatedwith privates circles
            return queryset.exclude( Q( circle__status__iexact='private' ) )


from djangoldp.permissions import ReadAndCreate
from djangoldp_resource.filters import ResourceFilterBackend


class ResourcePermissions(ReadAndCreate):
    with_cache = False
    filter_backends = [ResourceFilterBackend]
    
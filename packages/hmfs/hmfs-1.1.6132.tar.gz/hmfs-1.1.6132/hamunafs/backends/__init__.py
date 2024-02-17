from .base import BackendBase
from .bk_qiniu import Qiniu
from .bk_wy import WYSF
from .bk_minio import MinioBackend

backend_factory = {
    'qiniu': Qiniu,
    'wysf': WYSF,
    'minio': MinioBackend
}


from Source.Source_aggregate.Bearing.Architectures.CWRUFileArchitectures import (
    CWRUFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.FM6FileArchitectures import (
    FM6FileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.HitwzcFileArchitectures import (
    HitwzcFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.HUSTFileArchitectures import (
    HUSTFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.JNUFileArchitectures import (
    JNUFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.KAtFileArchitectures import (
    KAtFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.MFPTFileArchitectures import (
    MFPTFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.MultiDomainFileArchitectures import (
    MultiDomainFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.SCAFileArchitectures import (
    SCAFileArchitectures,
)
from Source.Source_aggregate.Bearing.Architectures.XJTU_SYFileArchitectures import (
    XJTU_SYFileArchitectures,
)

bind_classess = {
    'CWRU': CWRUFileArchitectures,
    'fm6xzxnf36-2': FM6FileArchitectures,
    'HUST': HUSTFileArchitectures,
    'JNU': JNUFileArchitectures,
    'KAt': KAtFileArchitectures,
    'MFPT': MFPTFileArchitectures,
    'Multi-domain': MultiDomainFileArchitectures,
    'SCA': SCAFileArchitectures,
    'hitwzc': HitwzcFileArchitectures,
    'XJTU-SY':XJTU_SYFileArchitectures,
}


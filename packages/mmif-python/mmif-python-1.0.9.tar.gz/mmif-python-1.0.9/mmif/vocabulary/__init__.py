from .base_types import ThingTypesBase
from .base_types import ThingType
from .base_types import ClamsTypesBase
from .base_types import AnnotationTypesBase
from .base_types import DocumentTypesBase
from .annotation_types import AnnotationTypes
from .document_types import DocumentTypes

typevers = {**ThingType.typevers, **AnnotationTypes.typevers, **DocumentTypes.typevers}

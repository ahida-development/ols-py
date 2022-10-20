from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import constr

EntityType = Literal["class", "property", "individual", "ontology"]

# MyPy doesn't play nice with pydantic's constrained types,
#   see https://github.com/pydantic/pydantic/issues/3080
if TYPE_CHECKING:
    AnnotationFieldName = str
else:
    AnnotationFieldName = constr(regex=r"^\w+_annotation$")

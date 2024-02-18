from pydantic import BaseModel
from typing import Optional, List
from enum import IntEnum

class OrganicProductionType(IntEnum):
    Conventional = 0
    Organic = 1
    Undetermined = 2
    
class FADNProductJsonDTO(BaseModel):
    fadnIdentifier: str
    description: str
    productType: str
    arable: bool
    
class PolicyJsonDTO(BaseModel):
    policyIdentifier: str
    isCoupled: bool
    policyDescription: str
    
class ProductGroupJsonDTO(BaseModel):
    name: str
    productType: str
    originalNameDatasource: str
    productsIncludedInOriginalDataset: str
    modelSpecificCategories: List[str]
    organic: OrganicProductionType
    fadnProducts: List[FADNProductJsonDTO]
    policies: List[PolicyJsonDTO]
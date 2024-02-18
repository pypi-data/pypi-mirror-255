from pydantic import BaseModel
from typing import Optional, List
from enum import IntEnum
from agricore_sp_models.common_models import OrganicProductionType, ProductGroupJsonDTO
    
class AgriculturalProduction(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    productGroupId: Optional[int] = None
    valueSales: float
    quantitySold: float
    cropProduction: float
    irrigatedArea: float
    cultivatedArea: float
    organicProductionType: OrganicProductionType
    variableCosts: float
    landValue: float
    sellingPrice: float
    
class AgriculturalProductionDTO(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    productGroupId: Optional[int] = None
    valueSales: float
    quantitySold: float
    cropProduction: float
    irrigatedArea: float
    cultivatedArea: float
    organicProductionType: OrganicProductionType
    variableCosts: float
    landValue: float
    sellingPrice: float
    
class LivestockProduction(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    productGroupId: Optional[int] = None
    numberOfAnimals: float
    numberOfAnimalsSold: int
    valueSoldAnimals: float
    numberAnimalsForSlaughtering: int
    valueSlaughteredAnimals: float
    numberAnimalsRearingBreading: float
    valueAnimalsRearingBreading: float
    milkTotalProduction: float
    milkProductionSold: float
    milkTotalSales: float
    milkVariableCosts: float
    woolTotalProduction: float
    woolProductionSold: float
    eggsTotalSales: float
    eggsTotalProduction: float
    eggsProductionSold: float
    manureTotalSales: float
    dairyCows: int
    variableCosts: float

class Population(BaseModel):
    id: Optional[int] = None
    description: str

class SyntheticPopulation(BaseModel):
    id: Optional[int] = None
    populationId: int
    yearId: int
    description: str
    name: str
    
class Farm(BaseModel):
    id: Optional[int] = None
    populationId: Optional[int] = None
    lat: int
    long: int
    altitude: int
    regionLevel1: str
    regionLevel1Name: str
    regionLevel2: str
    regionLevel2Name: str
    regionLevel3: int
    regionLevel3Name: str
    farmCode: str
    technicalEconomicOrientation: int
    weight_ra: float
    weight_reg: float
        
class ProductGroup(BaseModel):
    id: Optional[int] = None
    populationId: Optional[int] = None
    name: str
    productType: int
    originalNameDatasource: str
    productsIncludedInOriginalDataset: str
    organic: OrganicProductionType
    modelSpecificCategories: List[str]
    
class FADNProductRelation(BaseModel):
    id: Optional[int] = None
    productGroupId: Optional[int] = None
    fadnProductId: Optional[int] = None
    populationId: Optional[int] = None

class ClosingValue(BaseModel):
    id: Optional[int] = None
    agriculturalLandArea: float
    agriculturalLandValue: float
    plantationsValue: float
    landImprovements: float
    forestLandArea: float
    forestLandValue: float
    farmBuildingsValue: float
    machineryAndEquipment: float
    intangibleAssetsTradable: float
    intangibleAssetsNonTradable: float
    otherNonCurrentAssets: float
    longAndMediumTermLoans: float
    totalCurrentAssets: float
    farmNetIncome: float
    grossFarmIncome: float
    subsidiesOnInvestments: float
    vatBalanceOnInvestments: float
    totalOutputCropsAndCropProduction: float
    totalOutputLivestockAndLivestockProduction: float
    otherOutputs: float
    totalIntermediateConsumption: float
    taxes: float
    vatBalanceExcludingInvestments: float
    fixedAssets: float
    depreciation: float
    totalExternalFactors: float
    machinery: float
    farmId: int
    yearId: int
    
class Policy(BaseModel):
    id: Optional[int] = None
    policyIdentifier: str
    policyDescription: str
    isCoupled: bool
    
class PolicyProductGroupRelation(BaseModel):
    id: Optional[int] = None
    productGroupId: int
    policyId: int
    populationId: Optional[int] = None

class HolderFarmYearData(BaseModel):
    id: Optional[int] = None
    farmId: Optional[int] = None
    yearId: Optional[int] = None
    holderAge: int
    holderGender: int
    holderSuccessors: int
    holderSuccessorsAge: int
    holderFamilyMembers: int
    
class FarmYearSubsidy(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    policyId: int
    value: float

class ValueToLPDTO(BaseModel):
    farmId: int
    yearId: int
    a_0: float
    sE465: float
    sE490: float
    averageHAPrice: float
    sE420: float
    sE410: float
    aversionRiskFactor: float
    m_0: float

class CropDataDTO(BaseModel):
    cropProductiveArea: float
    cropVariableCosts: float
    quantitySold: float
    cropSellingPrice: float
    coupledSubsidy: float
    uaa: float
    rebreedingCows: float
    dairyCows: float

class DecoupledSubsidiesDTO(BaseModel):
    pGreen: float
    pBasic: float
    pPension: float

class ValueFromSPDTO(BaseModel):
    farmId: int
    totalCurrentAssets: float
    farmNetIncome: float
    farmGrossIncome: float
    agriculturalLand: float
    crops: dict[str,CropDataDTO]
    totalVariableCosts: float
    rentBalanceArea: float
    decoupledSubsidies: DecoupledSubsidiesDTO

class LivestockDTO(BaseModel):
    numberOfAnimals: float
    dairyCows: int
    rebreedingCows: float
    milkProduction: float
    milkSellingPrice: float
    variableCosts: float

class HolderInfoDTO(BaseModel):
    holderAge: int
    holderSuccessorsAge: int
    holderSuccessors: int
    holderFamilyMembers: int

class AltitudeEnum(IntEnum):
    MOUNTAINS = 1
    HILLS = 2
    PLAINS = 3

class ValueToSPDTO(BaseModel):
    farmCode: int
    holderInfo: Optional[HolderInfoDTO] = None
    cod_RAGR: str
    cod_RAGR2: str
    cod_RAGR3: int
    technicalEconomicOrientation: int
    altitude: AltitudeEnum
    currentAssets: float
    decoupledSubsidies: Optional[DecoupledSubsidiesDTO] = None
    crops: dict[str,CropDataDTO]
    livestock: Optional[LivestockDTO] = None

class DataToSPDTO(BaseModel):
    values: List[ValueToSPDTO]
    productGroups: List[ProductGroupJsonDTO]
    coupledSubsidiesProductGroupsDict: dict[str,str]

class IntermediateValueFromLP(BaseModel):
    farmId: int
    averageHAPrice: float
    previousAgriculturalLand: float
    result: dict

class LandTransaction(BaseModel):
    productionId: int
    destinationFarmId: int
    yearId: int
    percentage: float
    salePrice: float

class AgroManagementDecisions(BaseModel):
    farmId: int
    yearId: int
    agriculturalLand: float
    longAndMediumTermLoans: float
    totalCurrentAssets: float
    averageLandValue: float
    targetedLandAquisitionArea: float
    targetedLandAquisitionHectarPrice: float
    retireAndHandOver: bool

class AgroManagementDecisionFromLP(BaseModel):
    agroManagementDecisions: List[AgroManagementDecisions]
    landTransactions: List[LandTransaction]
    errorList: List[int]

class DataToLPDTO(BaseModel):
    values: List[ValueToLPDTO]
    agriculturalProductions: List[AgriculturalProductionDTO]
    ignoreLP: Optional[bool]
    ignoreLMM: Optional[bool]


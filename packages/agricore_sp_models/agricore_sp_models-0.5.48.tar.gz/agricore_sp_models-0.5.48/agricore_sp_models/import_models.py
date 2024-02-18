from agricore_sp_models.common_models import OrganicProductionType, ProductGroupJsonDTO
from pydantic import BaseModel, Field
from typing import List

class AgriculturalProductionJsonDTO(BaseModel):
    yearNumber: int
    productName: str 
    organicProductionType: OrganicProductionType
    cultivatedArea: float
    irrigatedArea: float 
    cropProduction: float
    quantitySold: float
    valueSales: float 
    variableCosts: float 
    landValue: float 
    sellingPrice: float

class LivestockProductionJsonDTO(BaseModel):
    yearNumber: int
    productName: str
    numberOfAnimals: float
    dairyCows: int
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
    variableCosts: float
    sellingPrice: float
    
class HolderFarmYearDataJsonDTO(BaseModel):
    yearNumber: int
    holderAge: int
    holderFamilyMembers: int
    holderSuccessorsAge: int
    holderGender: str
    holderSuccessors: int
    
class ClosingValFarmValueDTO(BaseModel):
    agriculturalLandArea: float
    agriculturalLandValue: float
    agriculturalLandHectaresAdquisition: float
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
    yearNumber: int
    rentBalance: float

class FarmYearSubsidyDTO(BaseModel):
    yearNumber: int
    value: float
    policyIdentifier: str
    
class LandTransactionJsonDTO(BaseModel):
    yearNumber: int
    productGroupName: str
    destinationFarmCode: str
    originFarmCode: str
    percentage: float = Field(..., ge=0, le=1)
    salePrice: float
    
class FarmJsonDTO(BaseModel):
    farmCode: str
    lat: int
    long: int
    altitude: str = ""
    regionLevel1: str
    regionLevel1Name: str = ""
    regionLevel2: str
    regionLevel2Name: str = ""
    regionLevel3: str
    regionLevel3Name: str = ""
    technicalEconomicOrientation: int
    agriculturalProductions: List[AgriculturalProductionJsonDTO]
    livestockProductions: List[LivestockProductionJsonDTO]
    holderFarmYearsData: List[HolderFarmYearDataJsonDTO]
    closingValFarmValues: List[ClosingValFarmValueDTO]
    farmYearSubsidies: List[FarmYearSubsidyDTO]
    landTransactions: List[LandTransactionJsonDTO]
    
    
class PopulationJsonDTO(BaseModel):
    description: str = ""
    farms: List[FarmJsonDTO]
    productGroups: List[ProductGroupJsonDTO]

class SyntheticPopulationJsonDTO(BaseModel):
    description: str = ""
    name: str = ""
    yearNumber: int
    population: PopulationJsonDTO
    

    

    

    

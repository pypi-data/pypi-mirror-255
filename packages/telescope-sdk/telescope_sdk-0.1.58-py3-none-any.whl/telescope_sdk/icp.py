from typing import List, Optional
from pydantic import BaseModel
from telescope_sdk.common import TelescopeBaseType
from telescope_sdk.locations import FilterableLocation
from telescope_sdk.company import CompanySizeRange, FoundedYearRange, RevenueRange


class ExampleCompany(BaseModel):
    id: str
    name: str


class IdealCustomerProfile(TelescopeBaseType):
    name: Optional[str] = None
    campaign_id: str
    example_companies: List[ExampleCompany]
    fictive_example_company_descriptions: Optional[List[str]] = []
    full_company_descriptive_info: Optional[str] = None
    summary_company_descriptive_info: Optional[str] = None
    full_contact_descriptive_info: Optional[str] = None
    summary_contact_descriptive_info: Optional[str] = None
    job_titles: List[str]
    keywords: List[str] = None
    negative_keywords: List[str] = None
    hq_location_filters: Optional[List[FilterableLocation]] = None
    employee_location_filters: Optional[List[FilterableLocation]] = None
    industries: List[str] = None
    company_size_range: CompanySizeRange = None
    company_types: List[str] = None
    founded_year_range: Optional[FoundedYearRange] = None
    special_criteria: Optional[List[str]] = []
    require_email: Optional[bool] = False
    company_revenue_range: Optional[RevenueRange] = None
    only_show_verified_emails: Optional[bool] = False
    hide_companies_in_another_campaign: Optional[bool] = False
    hide_leads_in_another_campaign: Optional[bool] = False
    deleted_at: Optional[str] = None

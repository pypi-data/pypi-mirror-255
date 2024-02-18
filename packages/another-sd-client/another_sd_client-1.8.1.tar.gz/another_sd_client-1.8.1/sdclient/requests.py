from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import root_validator


class SDRequest(BaseModel):
    class Config:
        frozen = True

    def get_name(self):
        raise NotImplementedError("Method must be implemented in subclasses")

    def to_query_params(self):
        params = self.dict()

        # Convert dates to SD date strings
        date_fields = {
            k: v.strftime("%d.%m.%Y") for k, v in params.items() if isinstance(v, date)
        }
        params.update(date_fields)

        # Remove empty fields and convert remaining fields to strings
        params = {k: str(v) for k, v in params.items() if v is not None}

        return params


class GetDepartmentRequest(SDRequest):
    """
    Query parameters for SDs GetDepartment20111201 endpoint
    """

    InstitutionIdentifier: Optional[str]
    InstitutionUUIDIdentifier: Optional[UUID]
    DepartmentIdentifier: Optional[str]
    DepartmentUUIDIdentifier: Optional[UUID]
    ActivationDate: date
    DeactivationDate: date
    # ContactInformationIndicator: bool = False
    DepartmentNameIndicator: bool = False
    # EmploymentDepartmentIndicator: bool = False
    PostalAddressIndicator: bool = False
    ProductionUnitIndicator: Optional[bool]
    UUIDIndicator: bool = False

    # TODO: check what is actually required
    @root_validator  # type: ignore
    def check_values(cls, values):
        institution_identifier = values.get("InstitutionIdentifier")
        institution_uuid_identifier = values.get("InstitutionUUIDIdentifier")
        department_identifier = values.get("DepartmentIdentifier")
        department_uuid_identifier = values.get("DepartmentUUIDIdentifier")
        postal_address_indicator = values.get("PostalAddressIndicator")
        production_unit_indicator = values.get("ProductionUnitIndicator")

        if institution_identifier is None and institution_uuid_identifier is None:
            raise ValueError(
                "Exactly one of InstitutionIdentifier or InstitutionUUIDndentifier can be set"
            )
        if (
            institution_identifier is not None
            and institution_uuid_identifier is not None
        ):
            raise ValueError(
                "Only one of InstitutionIdentifier and InstitutionUUIDIdentifier can be set"
            )
        if department_identifier is not None and department_uuid_identifier is not None:
            raise ValueError(
                "Only one of DepartmentIdentifier and DepartmentUUIDIdentifier can be set"
            )
        if production_unit_indicator and not postal_address_indicator:
            raise ValueError(
                "ProductionUnitIndicator requires PostalAddressIndicator to be true"
            )

        return values

    def get_name(self):
        return "GetDepartment"


class GetEmploymentRequest(SDRequest):
    """
    Query parameters for SDs GetEmployment20111201 endpoint
    """

    InstitutionIdentifier: str
    EffectiveDate: date

    PersonCivilRegistrationIdentifier: Optional[str]
    EmploymentIdentifier: Optional[str]
    DepartmentIdentifier: Optional[str]
    DepartmentLevelIdentifier: Optional[str]
    StatusActiveIndicator: bool = True
    StatusPassiveIndicator: bool = False
    DepartmentIndicator: bool = False
    EmploymentStatusIndicator: bool = False
    ProfessionIndicator: bool = False
    SalaryAgreementIndicator: bool = False
    SalaryCodeGroupIndicator: bool = False
    WorkingTimeIndicator: bool = False
    UUIDIndicator: bool = False

    # TODO: add validator (not enough to set StatusActiveIndicator...)
    def get_name(self):
        return "GetEmployment"


class GetOrganizationRequest(SDRequest):
    """
    Query parameters for SDs GetOrganization20111201 endpoint
    """

    InstitutionIdentifier: str | None = None
    InstitutionUUIDIdentifier: UUID | None = None
    ActivationDate: date
    DeactivationDate: date
    UUIDIndicator: bool = False

    @root_validator  # type: ignore
    def check_values(cls, values):
        institution_identifier = values.get("InstitutionIdentifier")
        institution_uuid_identifier = values.get("InstitutionUUIDIdentifier")
        activation_date = values.get("ActivationDate")
        deactivation_date = values.get("DeactivationDate")

        # Ensure that exactly one of "InstitutionIdentifier" and
        # "InstitutionUUIDIdentifier" is set
        if institution_identifier is None and institution_uuid_identifier is None:
            raise ValueError(
                "Exactly one of InstitutionIdentifier or InstitutionUUIDndentifier can be set"
            )
        if (
            institution_identifier is not None
            and institution_uuid_identifier is not None
        ):
            raise ValueError(
                "Only one of InstitutionIdentifier and InstitutionUUIDIdentifier can be set"
            )

        # Ensure that "ActivationDate" is before "DeactivationDate"
        if not activation_date <= deactivation_date:
            raise ValueError(
                "ActivationDate must be less than or equal to DeactivationDate"
            )

        return values

    def get_name(self):
        return "GetOrganization"

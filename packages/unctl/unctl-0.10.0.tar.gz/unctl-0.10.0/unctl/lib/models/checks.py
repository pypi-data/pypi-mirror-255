from dataclasses import field
from pydantic import BaseModel


class Code(BaseModel):
    """
    Check's remediation information using IaC like CloudFormation,
    Terraform or the native CLI
    """

    NativeIaC: str
    Terraform: str
    CLI: str
    Other: str


class Recommendation(BaseModel):
    """Check's recommendation information"""

    Text: str
    Url: str


class Remediation(BaseModel):
    """Check's remediation: Code and Recommendation"""

    Code: Code
    Recommendation: Recommendation


class CheckMetadataModel(BaseModel):
    """
    Check Metadata Model. It contains metadata from individual check json config
    """

    Enabled: bool = field(default=True)
    Provider: str
    CheckID: str
    CheckTitle: str
    CheckType: list[str]
    ServiceName: str
    SubServiceName: str
    ResourceIdTemplate: str
    Severity: str
    ResourceType: str
    Description: str
    Risk: str
    RelatedUrl: str
    Remediation: Remediation
    Categories: list[str]
    DependsOn: list[str]
    RelatedTo: list[str]
    Notes: str
    Cli: str | list[str]
    PositiveMatch: str
    NegativeMatch: str
    DiagnosticClis: list[str | list[str]]

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, TypeVar

from kimai.jsonserializer import JsonSerializable

T = TypeVar("T", bound="JsonSerializable")


@dataclass
class UserInfo(JsonSerializable):
    apiToken: bool
    initials: str
    id: int
    alias: str
    title: Optional[str]
    username: str
    accountNumber: Optional[str]
    enabled: bool
    color: Optional[str]


@dataclass
class CustomerInfo(JsonSerializable):
    id: int
    name: str
    number: str
    comment: Optional[str]
    visible: bool
    billable: bool
    company: Optional[str]
    vatId: Optional[str]
    contact: Optional[str]
    address: Optional[str]
    country: str
    currency: str
    phone: Optional[str]
    fax: Optional[str]
    mobile: Optional[str]
    email: Optional[str]
    homepage: Optional[str]
    timezone: str
    metaFields: List
    teams: List
    budget: float
    timeBudget: float
    budgetType: Optional[str]
    color: str


@dataclass
class ProjectInfo(JsonSerializable):
    parentTitle: str
    customer: int
    id: int
    name: str
    start: str
    end: Optional[str]
    comment: Optional[str]
    visible: bool
    billable: bool
    metaFields: List
    teams: List
    globalActivities: bool
    number: str
    color: str


@dataclass
class TimeEntry(JsonSerializable):
    activity: int
    project: int
    user: int
    tags: List
    id: int
    begin: str
    end: str
    duration: Fraction
    description: Optional[str]
    rate: Fraction
    internalRate: Fraction
    exported: bool
    billable: bool
    metaFields: List


@dataclass
class TimeEntryFull(JsonSerializable):
    activity: int
    project: int
    user: int
    tags: List
    id: int
    begin: str
    end: str
    duration: Fraction
    description: Optional[str]
    rate: Fraction
    hourlyRate: Fraction
    internalRate: Fraction
    exported: bool
    billable: bool
    metaFields: List


@dataclass
class ActivityInfo(JsonSerializable):
    parentTitle: Optional[str]
    project: Optional[int]
    id: int
    name: str
    comment: Optional[str]
    visible: bool
    billable: bool
    metaFields: List
    teams: List
    number: str
    budget: float
    timeBudget: float
    budgetType: Optional[str]
    color: str

from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from enum import Enum
from typing import Any, Tuple, List, Callable, TypeVar, Generic
from collections import namedtuple


@dataclass
class PasswordSettings:
    length: int
    special_characters: str
    order_list: list[str]
    special_characters_count: int
    alphabets_lowercase_count: int
    alphabets_uppercase_count: int
    digits_count: int = 1
    shuffled: bool = False


@dataclass
class NameCaption:
    name: str
    caption: str | None = None


@dataclass
class NameCaptionDescription(NameCaption):
    description: str | None = None


@dataclass
class OrderedNameCaptionDescription(NameCaptionDescription):
    order: int | None = None


@dataclass
class IconedOrderedNameCaptionDescription(OrderedNameCaptionDescription):
    icon: str | None = None


@dataclass
class ParamItem(NameCaptionDescription):
    optional: bool = False

    visible: bool = True
    saved: bool = True
    key: bool = False

    def configurate(
        self,
        visible: bool | None = None,
        saved: bool | None = None,
        key: bool | None = None,
    ) -> Any:
        result: ParamItem = ParamItem(
            self.name, self.caption, self.description, self.optional
        )
        if visible is not None:
            result.visible = visible
        if saved is not None:
            result.saved = saved
        if key is not None:
            result.key = key
        return result


@dataclass
class FieldItem:
    name: str | None = None
    caption: str | None = None
    visible: bool = True
    class_type: Any | None = None
    default_value: str | None = None
    data_formatter: str = "{data}"


class FieldItemList:
    list: list[FieldItem]

    def copy_field_item(self, value: FieldItem) -> FieldItem:
        return FieldItem(
            value.name,
            value.caption,
            value.visible,
            value.class_type,
            value.default_value,
            value.data_formatter,
        )

    def __init__(self, *args):
        self.list = []
        arg_list = list(args)
        for arg_item in arg_list:
            if isinstance(arg_item, FieldItem):
                item: FieldItem = self.copy_field_item(arg_item)
                self.list.append(item)
            elif isinstance(arg_item, FieldItemList):
                for item in arg_item.list:
                    self.list.append(self.copy_field_item(item))
            elif isinstance(arg_item, list):
                self.list.extend(arg_item)

    def get_list(self) -> list[FieldItem]:
        return self.list

    def get_item_and_index_by_name(self, value: str) -> Tuple[FieldItem, int]:
        index: int = -1
        result: FieldItem | None = None
        for item in self.list:
            index += 1
            if item.name == value:
                result = item
                break
        return result, -1 if result is None else index

    def get_item_by_name(self, value: str) -> FieldItem:
        result, _ = self.get_item_and_index_by_name(value)
        return result

    def position(self, name: str, position: int):
        _, index = self.get_item_and_index_by_name(name)
        if index != -1:
            self.list.insert(position, self.list.pop(index))
        return self

    def get_name_list(self):
        return list(map(lambda item: str(item.name), self.list))

    def get_caption_list(self):
        return list(
            map(lambda x: str(x.caption), filter(lambda y: y.visible, self.list))
        )

    def visible(self, name: str, value: bool):
        item, _ = self.get_item_and_index_by_name(name)
        if item is not None:
            item.visible = value
        return self

    def caption(self, name: str, value: bool):
        item, _ = self.get_item_and_index_by_name(name)
        if item is not None:
            item.caption = value
        return self

    def length(self) -> int:
        return len(self.list)


T = TypeVar("T")
R = TypeVar("R")


@dataclass
class Result(Generic[T]):
    fields: FieldItemList | None = None
    data: T | None = None

    def __len__(self):
        return len(self.data)

    def __iadd__(self, value):
        if (
            isinstance(value, Result)
            and isinstance(self.data, list)
            and isinstance(value.data, list)
        ):
            self.data += value.data
        return self

    def __add__(self, value):
        if (
            isinstance(value, Result)
            and isinstance(self.data, list)
            and isinstance(value.data, list)
        ):
            self.data += value.data
        return self


@dataclass
class FullName:
    last_name: str = ""
    first_name: str = ""
    middle_name: str = ""

    def as_list(self) -> list[str]:
        return [self.last_name, self.first_name, self.middle_name]


@dataclass
class UserBase:
    name: str | None = None
    description: str | None = None
    distinguishedName: str | None = None


@dataclass
class User(UserBase):
    samAccountName: str | None = None
    mail: str | None = None
    telephoneNumber: str | None = None
    userAccountControl: int | None = None


Rect = namedtuple("Rect", ["left", "top", "width", "height"])


@dataclass
class IndicationDevice:
    name: str | None = None
    description: str | None = None
    ip_address: tuple[str, int] | None = None


@dataclass
class MailboxInfo:
    timestamp: datetime | None = None
    last_uid: str | None = None


@dataclass
class NewMailMessage:
    mailbox_address: str | None = None
    subject: str | None = None
    text: str | None = None
    from_: str | None = None


@dataclass
class RecipientWaitingForInput:
    group_name: str | None = None
    timeout: int | None = None
    recipient: str | None = None
    timestamp: datetime | None = None


@dataclass
class BarcodeInformation:
    data: str | None = None
    type: str | None = None
    rect: Rect | None = None


@dataclass
class EmailInformation:
    email: str | None = None
    person_pin: int = 0
    person_name: str | None = None


@dataclass
class InaccesableEmailInformation(EmailInformation):
    workstation_name: str | None = None
    registrator_person_name: str | None = None


@dataclass
class CardRegistryFolderPosition:
    ChartFolder: str | None = None
    p_a: int = 0
    p_b: int = 0
    p_c: int = 0


@dataclass
class ActionValue:
    caption: str
    value: str


@dataclass
class LoginPasswordPair:
    login: str | None = None
    password: str | None = None


@dataclass
class OGRN:
    name: str | None = None
    code: str | None = None
    data: dict | None = None


@dataclass
class ComputerDescription:
    name: str | None = None
    properties: int = 0
    description: str | None = None


@dataclass
class Computer(ComputerDescription):
    samAccountName: str | None = None
    accessable: bool | None = None


@dataclass
class Server(Computer):
    pass


@dataclass
class Workstation(Computer):
    pass


@dataclass
class ResourceDescription:
    address: str | None = None
    name: str | None = None
    inaccessibility_check_values: tuple[int] = (2, 20, 15)


@dataclass
class ResourceDescriptionDelegated(ResourceDescription):
    delegator: str | None = None


@dataclass
class SiteResourceDescription(ResourceDescription):
    check_certificate_status: bool = False
    check_free_space_status: bool = False
    driver_name: str | None = None
    internal: bool = False


class IResourceStatus:
    pass


@dataclass
class ResourceStatus(ResourceDescription, IResourceStatus):
    accessable: bool | None = None
    inaccessibility_counter: int = 0


@dataclass
class WSResourceStatus(ResourceStatus):
    pass


@dataclass
class ServerResourceStatus(ResourceStatus):
    pass


@dataclass
class DiskStatistics:
    name: str | None = None
    free_space: int | None = None
    size: int | None = None


@dataclass
class DisksResourceStatus(IResourceStatus):
    host: str | None = None
    disk_list: list[DiskStatistics] = field(default_factory=list)


@dataclass
class SiteResourceStatus(ResourceStatus, SiteResourceDescription):
    certificate_status: str | None = None
    free_space_status: str | None = None


@dataclass
class MarkPerson:
    FullName: str | None = None
    TabNumber: str | None = None


@dataclass
class MarkPersonDivision(MarkPerson):
    DivisionName: str | None = None
    DivisionID: int | None = None


@dataclass
class TemporaryMark(MarkPerson):
    OwnerTabNumber: str | None = None


@dataclass
class PolibasePersonBase:
    pin: int | None = None
    FullName: str | None = None
    telephoneNumber: str | None = None


@dataclass
class PolibasePerson(PolibasePersonBase):
    Birth: datetime | None = None
    Comment: str | None = None
    ChartFolder: str | None = None
    email: str | None = None
    barcode: str | None = None
    registrationDate: datetime | None = None
    telephoneNumber2: str | None = None
    telephoneNumber3: str | None = None
    telephoneNumber4: str | None = None


@dataclass
class PolibaseNote:
    emailed: str | None = None


@dataclass
class PolibasePersonVisitDS(PolibasePersonBase):
    id: int | None = None
    registrationDate: str | None = None
    beginDate: str | datetime | None = None
    completeDate: str | datetime | None = None
    status: int | None = None
    cabinetID: int | None = None
    doctorID: int | None = None
    doctorFullName: str | None = None
    serviceGroupID: int | None = None


@dataclass
class CardRegistryFolderStatistics:
    name: str | None = None
    count: int = 0


@dataclass
class PolibasePersonVisitSearchCritery:
    vis_no: Any | None = None
    vis_pat_no: Any | None = None
    vis_pat_name: Any | None = None
    vis_place: Any | None = None
    vis_reg_date: Any | None = None
    vis_date_ps: Any | None = None
    vis_date_pf: Any | None = None
    vis_date_fs: Any | None = None
    vis_date_ff: Any | None = None


@dataclass
class PolibasePersonVisitNotificationDS:
    visitID: int | None = None
    messageID: int | None = None
    type: int | None = None


@dataclass
class EventDS:
    name: str | None = None
    parameters: dict | None = None
    timestamp: datetime | date | str | int | None = None
    id: int = 0


@dataclass
class Message:
    message: str | None = None
    recipient: str | None = None
    sender: str | None = None


@dataclass
class DelayedMessage(Message):
    date: Any | None = None
    type: int | None = None


@dataclass
class DelayedMessageDS(DelayedMessage):
    id: int | None = None
    status: int | None = None


@dataclass
class MessageSearchCritery:
    id: Any | None = None
    recipient: str | None = None
    date: datetime | str | None = None
    type: Any | None = None
    status: int | None = None
    sender: str | None = None


@dataclass
class PolibasePersonNotificationConfirmation:
    recipient: str | None = None
    sender: str | None = None
    status: int = 0


@dataclass
class PolibasePersonVisitNotification(
    PolibasePersonVisitDS, PolibasePersonVisitNotificationDS
):
    pass


@dataclass
class PolibasePersonVisit(PolibasePersonVisitDS):
    registrationDate: datetime | None = None
    beginDate: datetime | None = None
    completeDate: datetime | None = None
    beginDate2: datetime | None = None
    completeDate2: datetime | None = None


@dataclass
class PolibasePersonQuest:
    step: int | None = None
    stepConfirmed: bool | None = None
    timestamp: int | None = None


@dataclass
class PolibasePersonInformationQuest(PolibasePersonBase):
    confirmed: int | None = None
    errors: int | None = None


@dataclass
class PolibasePersonReviewQuest(PolibasePersonQuest):
    beginDate: str | None = None
    completeDate: str | None = None
    grade: int | None = None
    message: str | None = None
    informationWay: int | None = None
    feedbackCallStatus: int | None = None


@dataclass
class MarkGroup:
    GroupName: str | None = None
    GroupID: int | None = None


@dataclass
class Mark(MarkPersonDivision, MarkGroup):
    pID: int | None = None
    mID: int | None = None
    Comment: str | None = None
    telephoneNumber: str | None = None
    type: int | None = None


@dataclass
class PersonDivision:
    id: int | None = None
    name: str | None = None


@dataclass
class TimeTrackingEntity(MarkPersonDivision):
    TimeVal: str | None = None
    Mode: int | None = None


@dataclass
class TimeTrackingResultByDate:
    date: str | None = None
    enter_time: str | None = None
    exit_time: str | None = None
    duration: int | None = None


@dataclass
class TimeTrackingResultByPerson:
    tab_number: str | None = None
    full_name: str | None = None
    duration: int = 0
    list: List[TimeTrackingResultByDate] = field(default_factory=list)


@dataclass
class WhatsAppMessage:
    message: str | None = None
    from_me: bool | None = None
    sender: str | None = None
    recipient: str | None = None
    profile_id: str | None = None
    time: int | None = None
    chatId: str | None = None
    flags: int | None = None
    return_result_key: str | None = None
    args: tuple[Any] | None = None


@dataclass
class WhatsAppMessagePayload:
    title: str
    body: str


@dataclass
class WhatsAppMessageListPayload(WhatsAppMessagePayload):
    btn_text: str
    list: dict


@dataclass
class WhatsAppMessagebButton:
    body: str | None = None
    id: str | None = None


@dataclass
class WhatsAppMessageButtonsPayload(WhatsAppMessagePayload):
    buttons: list[WhatsAppMessagebButton] | None = None


@dataclass
class TimeTrackingResultByDivision:
    name: str
    list: List[TimeTrackingResultByPerson] = field(default_factory=list)


@dataclass
class RobocopyJobDescription:
    name: str | None = None
    start_datetime: str | None = None
    host: str | None = None
    run_from_system_account: bool = False
    run_with_elevetion: bool = False
    live: bool = False

    def clone(
        self,
        job_name: str,
        start_datetime: str | None = None,
        host: str | None = None,
        live: bool | None = None,
    ):
        return RobocopyJobDescription(
            job_name,
            start_datetime,
            host or self.host,
            self.run_from_system_account,
            self.run_with_elevetion,
            self.live if live is None else live,
        )


@dataclass
class RobocopyJobItem(RobocopyJobDescription):
    source: str | None = None
    destination: str | None = None


@dataclass
class RobocopyJobStatus:
    name: str | None = None
    source: str | None = None
    destination: str | None = None
    active: bool = False
    last_created: str | None = None
    last_status: int | None = None
    live: bool = False
    pid: int = -1


@dataclass
class PrinterADInformation:
    driverName: str | None = None
    adminDescription: str | None = None
    description: str | None = None
    portName: str | None = None
    serverName: str | None = None
    name: str | None = None


@dataclass
class IndicationsContainer:
    timestamp: datetime | None = None


@dataclass
class HumidityIndicationsValue:
    humidity: float | None = None


@dataclass
class TemparatureIndicationsValue:
    temperature: float | None = None


@dataclass
class TemperatureAndHumidityIndicationsValue(
    HumidityIndicationsValue, TemparatureIndicationsValue
):
    pass


@dataclass
class ChillerIndicationsValue(TemparatureIndicationsValue):
    indicators: int = 0


@dataclass
class ChillerIndicationsValueContainer(ChillerIndicationsValue, IndicationsContainer):
    pass


@dataclass
class CTIndicationsValue(TemperatureAndHumidityIndicationsValue):
    pass


@dataclass
class CTIndicationsValueContainer(CTIndicationsValue, IndicationsContainer):
    pass


@dataclass
class GKeepItem:
    name: str | None = None
    title: str | None = None
    id: str | None = None

@dataclass
class File:
    title: str | None = None
    text: str | None = None
    id: str | None = None

@dataclass
class Note(File):
    id: str | None = None
    images: list[str] | None = None


@dataclass
class InventoryReportItem:
    name: str | int | None = None
    inventory_number: str | None = None
    row: str | None = None
    quantity: int | None = None
    name_column: int | None = None
    inventory_number_column: int | None = None
    quantity_column: int | None = None


@dataclass
class PrinterStatus:
    ip: str | None = None
    description: str | None = None
    variant: str | None = None
    port: int | None = None
    community: str | None = None
    accessable: bool | None = None


@dataclass
class TimeSeriesStatistics:
    count: int = 0
    values: list[datetime] | None = None
    distance: list[timedelta] | None = None
    min: int | None = None
    max: int | None = None
    avg: int | None = None


@dataclass
class PrinterReport(PrinterStatus):
    name: str | None = None
    model: str | None = None
    serial: int | None = None
    adminDescription: str | None = None
    meta: str | None = None
    printsOverall: int | None = None
    printsColor: int | None = None
    printsMonochrome: int | None = None
    fuserType: int | None = None
    fuserCapacity: int | None = None
    fuserRemaining: int | None = None
    wasteType: int | None = None
    wasteCapacity: int | None = None
    wasteRemaining: int | None = None
    cleanerType: int | None = None
    cleanerCapacity: int | None = None
    cleanerRemaining: int | None = None
    transferType: int | None = None
    transferCapacity: int | None = None
    transferRemaining: int | None = None
    blackTonerType: str | None = None
    blackTonerCapacity: int | None = None
    blackTonerRemaining: int | None = None
    cyanTonerType: int | None = None
    cyanTonerCapacity: int | None = None
    cyanTonerRemaining: int | None = None
    magentaTonerType: int | None = None
    magentaTonerCapacity: int | None = None
    magentaTonerRemaining: int | None = None
    yellowTonerType: int | None = None
    yellowTonerCapacity: int | None = None
    yellowTonerRemaining: int | None = None
    blackDrumType: str | None = None
    blackDrumCapacity: int | None = None
    blackDrumRemaining: int | None = None
    cyanDrumType: int | None = None
    cyanDrumCapacity: int | None = None
    cyanDrumRemaining: int | None = None
    magentaDrumType: int | None = None
    magentaDrumCapacity: int | None = None
    magentaDrumRemaining: int | None = None
    yellowDrumType: int | None = None
    yellowDrumCapacity: int | None = None
    yellowDrumRemaining: int | None = None

    def get_toner(self, color: str) -> int:
        color = color.lower()
        remaining: int
        capacity: int
        if color == "c":
            remaining = self.cyanTonerRemaining
            capacity = self.cyanTonerCapacity
        if color == "m":
            remaining = self.magentaTonerRemaining
            capacity = self.magentaTonerCapacity
        if color == "y":
            remaining = self.yellowTonerRemaining
            capacity = self.yellowTonerCapacity
        if color == "k":
            remaining = self.blackTonerRemaining
            capacity = self.blackTonerCapacity
        try:
            if remaining == -1 or capacity == -1:
                return -1
            if remaining == -404 or capacity == -404:
                return -404
            if remaining == -401 or capacity == -401:
                return -401
            return int(round((int(remaining) / int(capacity)) * 100))
        except:
            return -1

    def get_drum(self, color: str) -> int:
        color = color.lower()
        if color == "c":
            remaining = self.cyanDrumRemaining
            capacity = self.cyanDrumCapacity
        if color == "m":
            remaining = self.magentaDrumRemaining
            capacity = self.magentaDrumCapacity
        if color == "y":
            remaining = self.yellowDrumRemaining
            capacity = self.yellowDrumCapacity
        if color == "k":
            remaining = self.blackDrumRemaining
            capacity = self.blackDrumCapacity
        try:
            if remaining == -1 or capacity == -1:
                return -1
            if remaining == -404 or capacity == -404:
                return -404
            if remaining == -401 or capacity == -401:
                return -401
            return int(round((int(remaining) / int(capacity)) * 100))
        except:
            return -1


@dataclass
class MarkGroupStatistics(MarkGroup):
    Comment: str | None = None
    Count: int | None = None


@dataclass
class EventDescription:
    message: str | Callable[[tuple[Any] | list[Any]], str] | None = None
    channel: Enum | None = None
    flags: int | tuple[Enum] | Enum | None = None
    params: tuple[ParamItem] | None = None


@dataclass
class ActionDescription:
    name: str | None = None
    alias: tuple[str] | None = None
    description: str | None = None
    question: str | None = None
    confirm: bool = True
    silence: bool = False
    parameters_description: str | None = None
    # parameters_default: tuple[str] | None = None
    forcable: bool = False
    forced_description: str | None = None


@dataclass
class ActionWasDone:
    action_description: str | None = None
    action: Enum | str | None = None
    user_name: str | None = None
    user_login: str | None = None
    parameters: list[Any] | None = None
    forced: bool = False


@dataclass
class StorageVariableHolder:
    key_name: str | None = None
    default_value: str | None = None
    description: str | None = None
    auto_init: bool = True
    # only for get
    section: str | None = None


@dataclass
class ExpiredTimestampVariableHolder:
    timestamp: str | None = None
    life_time: str | None = None
    resolver_note: str | None = None


@dataclass
class IntStorageVariableHolder(StorageVariableHolder):
    default_value: int = 0


@dataclass
class MinIntStorageVariableHolder(IntStorageVariableHolder):
    min_value: int = 0


@dataclass
class IntStorageVariableHolderWithMin(IntStorageVariableHolder):
    min_value: int = 0


@dataclass
class IntListStorageVariableHolder(StorageVariableHolder):
    default_value: list[int] | None = None


@dataclass
class FloatStorageVariableHolder(StorageVariableHolder):
    default_value: float | None = None


@dataclass
class BoolStorageVariableHolder(StorageVariableHolder):
    default_value: bool | None = None


@dataclass
class TimeStorageVariableHolder(StorageVariableHolder):
    default_value: str | None = None


@dataclass
class DateListStorageVariableHolder(StorageVariableHolder):
    default_value: list[str] | None = None


@dataclass
class StringListStorageVariableHolder(StorageVariableHolder):
    default_value: list[str] | None = None


@dataclass
class PolibaseDocument:
    file_path: str | None = None
    polibase_person_pin: int | None = None
    document_type: str | None = None


@dataclass
class MedicalDirectionDocument:
    number: int | None = None
    date: datetime | None = None
    person_name: str | None = None
    person_ensurence_number: str | None = None
    person_ensurence_agent: str | None = None
    person_birthday: datetime | str | None = None
    research_type: Enum | str | None = None
    research_code: str | None = None
    ogrn_number: str | None = None


@dataclass
class Titled:
    title: str


@dataclass
class ThresholdedText(Titled):
    threshold: float


@dataclass
class PolibaseDocumentDescription(ThresholdedText):
    title_top: int = 0
    title_height: int = 0
    page_count: int = 1


@dataclass
class DocumentDescription(ThresholdedText):
    left: float
    top: float
    right: float
    bottom: float


@dataclass
class MedicalResearchType:
    title_list: tuple[str] | None = None
    alias: str | None = None


@dataclass
class DirectoryInfo:
    value: str | None = None
    last_created_file_timestamp: float | None = None


@dataclass
class JournalRecord:
    # from pih.const import JournalType, Tags
    timestamp: datetime | None = None
    applicant_user: User | None = None
    type: Any | None = None
    tag: Any | None = None
    title: str | None = None
    text: str | None = None
    parameters: dict[str, Any] | None = None


@dataclass
class BonusInformation:
    all: float = 0
    spent: float = 0
    active: float = 0
    last_money_spent: float = 0
    last_spent: float = 0
    last: float = 0

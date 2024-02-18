import ipih

from pih.tools import ParameterList, BitMask as BM, j, n, nn, e, ne
from pih.consts import SUBSCRIBTION_TYPE
from pih.consts.errors import Error
from pih.collections.service import (
    Subscribtion,
    ServiceDescription,
    ServiceInformation,
    SubscribtionResult,
    SubscriberInformation,
    ServiceDescriptionBase,
    SubscribtionInformation,
)

from pih.tools import DataTool, OSTool, EnumTool
from pih.consts.rpc import RPC as CONST_RPC
from pih.tools.service import ServiceRoleTool, ServiceTool, ServiceAdminTool
from pih.consts.date_time import DATE_TIME
from pih.consts.service_commands import ServiceCommands as SC
import pih.rpc.rpcCommandCall_pb2_grpc as pb2_grpc
from pih.consts.service_roles import ServiceRoles
import pih.rpc.rpcCommandCall_pb2 as pb2

import sys
import grpc
import psutil
from grpc import Server
from threading import Thread
from typing import Any, Callable
from collections import defaultdict
from datetime import datetime, timedelta

STUB: ServiceDescription = ServiceDescription(name="Stub")


def GRPC_OPTIONS() -> list[tuple[str, int]]:
    size: int = 20 * 1024 * 1024
    return [
        ("grpc.max_receive_message_length", size),
        ("grpc.max_send_message_length", size),
    ]


class IService:
    def serve(
        self,
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
        call_handler: Callable[[str, ParameterList, Any], Any] | None = None,
        starts_handler: Callable[[Any | None], None] | None = None,
        max_workers: int | None = None,
        depends_on_list: list[ServiceRoles | ServiceDescription] | None = None,
        as_standalone: bool = False,
        show_output: bool = True,
    ) -> None:
        raise NotImplemented()

    def create_subscribtions(
        self, information: ServiceDescriptionBase | None = None
    ) -> None:
        raise NotImplemented()

    @property
    def subscribtions(self) -> list[SubscribtionInformation]:
        raise NotImplemented()

    def stop(self) -> Server:
        raise NotImplemented()

    def subscribe_on(
        self, sc: SC, type: int = SUBSCRIBTION_TYPE.ON_RESULT, name: str | None = None
    ) -> bool:
        raise NotImplemented()

    def unsubscribe(
        self, commnad_list: list[SC] | None = None, type: int | None = None
    ) -> bool:
        raise NotImplemented()

    def get_description(self) -> ServiceDescription:
        raise NotImplemented()


DEBUG: bool = False


class RPC:
    server: Server | None = None

    class SESSION:
        start_time: datetime
        life_time: timedelta
        thread_map: list[int] = []

    @staticmethod
    def create_service() -> IService:
        return RPC.Service()

    @staticmethod
    def create_error(context, message: str = "", code: Any | None = None) -> Any:
        context.set_details(message)
        context.set_code(code)
        return pb2.rpcCommandResult()

    class UnaryService(pb2_grpc.UnaryServicer):
        def __init__(
            self,
            service: IService,
            description: ServiceDescription,
            call_handler: Callable[[str, ParameterList, Any], Any] | None = None,
            *args,
            **kwargs,
        ):
            self.service_information = description
            self.call_handler = call_handler
            self.service = service
            self.subscriber_information_map: dict[
                SC, dict[str, SubscriberInformation]
            ] = defaultdict(dict)

        def internal_call_handler(
            self, command_name: str, parameters: Any, context
        ) -> Any:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A
            try:
                sc: SC | None = EnumTool.get(SC, command_name)
                parameter_list: ParameterList = ParameterList(parameters)
                if ne(sc):
                    if sc == SC.stop_service:
                        is_subscriber: bool = ServiceTool.is_service_as_listener(
                            self.service_information
                        )
                        if not is_subscriber:
                            RPC.call_service_command(
                                SC.on_service_stops, self.service_information
                            )
                        self.service.stop()
                        if not is_subscriber:
                            pid: int = OSTool.pid()
                            parent = psutil.Process(pid)
                            for child in parent.children(recursive=True):
                                child.kill()
                        return
                    if sc == SC.ping:
                        return DataTool.fill_data_from_source(
                            ServiceInformation(), self.service_information
                        )
                    if sc == SC.subscribe:
                        return self.subscribe_with_parameter_list(parameter_list)
                    if sc == SC.unsubscribe:
                        return self.unsubscribe_with_parameter_list(parameter_list)
                    if sc == SC.create_subscribtions:
                        self.service.create_subscribtions(
                            parameter_list.next(ServiceDescriptionBase())
                        )
                        return True
                    if sc == SC.update_service_information:
                        ServiceAdminTool.update_service_information(
                            parameter_list.next_as_list(ServiceInformation),
                            parameter_list.next(),
                        )
                        return True
                    if sc == SC.heart_beat:
                        date_string: str = A.D_Ex.parameter_list(parameter_list).get()
                        date: datetime = datetime.strptime(
                            date_string, DATE_TIME.ISO_DATETIME_FORMAT
                        )
                        parameter_list.set(0, date)
                        RPC.SESSION.life_time = date - RPC.SESSION.start_time
                return (
                    None
                    if e(self.call_handler)
                    else self.call_subscribers_after(
                        sc,
                        parameter_list,
                        self.call_handler(
                            command_name,
                            self.call_subscribers_before(sc, parameter_list),
                            context,
                        ),
                    )
                )
            except Exception as error:
                A.ER.global_except_hook(error)

        def unsubscribe_all(self) -> None:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A

            def unsubscribe_all_internal() -> None:
                for sc in self.subscriber_information_map:
                    for service_information_name in self.subscriber_information_map[sc]:
                        subscriber_information: SubscriberInformation = (
                            self.subscriber_information_map[sc][
                                service_information_name
                            ]
                        )
                        DataTool.rpc_unrepresent(
                            RPC.call_service(
                                subscriber_information.service_information,
                                SC.unsubscribe,
                                (sc, subscriber_information.name),
                            )
                        )
                self.subscriber_information_map = defaultdict(dict)

            Thread(target=unsubscribe_all_internal).start()

        def unsubscribe_with_parameter_list(self, value: ParameterList) -> None:
            description: ServiceDescription = value.next(ServiceDescription())
            role_description_name: str = description.name
            for service_command in self.subscriber_information_map:
                if (
                    role_description_name
                    in self.subscriber_information_map[service_command]
                ):
                    del self.subscriber_information_map[service_command][
                        role_description_name
                    ]

        def subscribe_with_parameter_list(self, value: ParameterList) -> bool:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A
            service_information: ServiceDescriptionBase = value.next(
                ServiceDescriptionBase()
            )
            subscribtion_information: SubscribtionInformation = value.next(
                SubscribtionInformation()
            )
            subscribtion_information.service_command = EnumTool.get(
                SC, subscribtion_information.service_command
            )
            return self.subscribe(service_information, subscribtion_information)

        def subscribe(
            self,
            service_description: ServiceDescription,
            subscribtion_information: SubscribtionInformation,
        ) -> bool:
            sc: SC = subscribtion_information.service_command
            name: str | None = subscribtion_information.name
            type: int = subscribtion_information.type
            if sc in self.subscriber_information_map:
                if service_description.name in self.subscriber_information_map[sc]:
                    subscriber_information: SubscriberInformation = (
                        self.subscriber_information_map[sc][service_description.name]
                    )
                    if (
                        subscriber_information.service_information
                        == service_description
                        and BM.has(subscriber_information.type, type)
                    ):
                        self.subscriber_information_map[sc][
                            service_description.name
                        ] = SubscriberInformation(
                            type, name, service_information=service_description
                        )
                else:
                    self.subscriber_information_map[sc][service_description.name] = (
                        SubscriberInformation(
                            type, name, service_information=service_description
                        )
                    )
            else:
                self.subscriber_information_map[sc][service_description.name] = (
                    SubscriberInformation(
                        type, name, service_information=service_description
                    )
                )
            return True

        def call_subscribers_before(self, sc: SC, in_result: ParameterList):
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A
            out_result: ParameterList = in_result
            if sc in self.subscriber_information_map:
                for service_information_name in list(
                    self.subscriber_information_map[sc]
                ):
                    subscriber_information: SubscriberInformation = (
                        self.subscriber_information_map[sc][service_information_name]
                    )
                    service_information: ServiceInformation = (
                        subscriber_information.service_information
                    )
                    if (
                        BM.has(
                            subscriber_information.type, SUBSCRIBTION_TYPE.ON_PARAMETERS
                        )
                        and subscriber_information.enabled
                    ):
                        subscriber_information.available = RPC.check_availability(
                            service_information
                        )
                        if subscriber_information.available:
                            out_result = ParameterList(
                                DataTool.rpc_unrepresent(
                                    RPC.call_service(
                                        service_information,
                                        sc,
                                        (
                                            in_result,
                                            SubscribtionResult(
                                                None,
                                                SUBSCRIBTION_TYPE.ON_PARAMETERS,
                                                True,
                                            ),
                                        ),
                                    )
                                )
                            )
                        else:
                            del self.subscriber_information_map[sc][
                                service_information_name
                            ]
            return out_result

        def call_subscribers_after(
            self, sc: SC, parameter_list: ParameterList, result: Any
        ) -> Any:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A

            def internal_call_subscribers_after_sequentially(
                sc: SC,
                subscriber_list: list[SubscriberInformation],
                parameter_list: ParameterList,
                result: Any,
            ):
                for subscriber in subscriber_list:
                    role_description_item: ServiceDescription = (
                        subscriber.service_information
                    )
                    subscriber.available = RPC.check_availability(role_description_item)
                    if subscriber.available:
                        result = RPC.call_service(
                            role_description_item,
                            sc,
                            (
                                parameter_list,
                                SubscribtionResult(
                                    result,
                                    SUBSCRIBTION_TYPE.ON_RESULT_SEQUENTIALLY,
                                    True,
                                ),
                            ),
                        )
                    else:
                        if DataTool.if_is_in(
                            self.subscriber_information_map[sc],
                            role_description_item.name,
                        ):
                            del self.subscriber_information_map[sc][
                                role_description_item.name
                            ]

            def internal_call_subscribers_after(
                sc: SC,
                subscriber_information: SubscriberInformation,
                parameter_list: ParameterList,
                result: Any,
            ):
                service_information: ServiceDescriptionBase = (
                    subscriber_information.service_information
                )
                subscriber_information.available = RPC.check_availability(
                    service_information
                )
                if subscriber_information.available:
                    RPC.call_service(
                        service_information,
                        sc,
                        (
                            parameter_list,
                            SubscribtionResult(
                                result, SUBSCRIBTION_TYPE.ON_RESULT, True
                            ),
                        ),
                    )
                else:
                    if service_information.name in self.subscriber_information_map[sc]:
                        del self.subscriber_information_map[sc][
                            service_information.name
                        ]

            if sc in self.subscriber_information_map:
                after_sequentially_subscriber_information_list: list[
                    SubscriberInformation
                ] = []
                for servce_information_name in list(
                    self.subscriber_information_map[sc]
                ):
                    subscriber_information: SubscriberInformation = (
                        self.subscriber_information_map[sc][servce_information_name]
                    )
                    if subscriber_information.enabled:
                        if BM.has(
                            subscriber_information.type, SUBSCRIBTION_TYPE.ON_RESULT
                        ):
                            Thread(
                                target=internal_call_subscribers_after,
                                args=(
                                    sc,
                                    subscriber_information,
                                    parameter_list,
                                    result,
                                ),
                            ).start()
                        elif BM.has(
                            subscriber_information.type,
                            SUBSCRIBTION_TYPE.ON_RESULT_SEQUENTIALLY,
                        ):
                            after_sequentially_subscriber_information_list.append(
                                subscriber_information
                            )
                if ne(after_sequentially_subscriber_information_list):
                    Thread(
                        target=internal_call_subscribers_after_sequentially,
                        args=(
                            sc,
                            after_sequentially_subscriber_information_list,
                            parameter_list,
                            result,
                        ),
                    ).start()

            return result

        def rpcCallCommand(self, command, context):
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A
            parameters = command.parameters
            if ne(parameters):
                parameters = DataTool.rpc_unrepresent(parameters)
            result: Any = self.internal_call_handler(command.name, parameters, context)
            if n(context.code()):
                return pb2.rpcCommandResult(data=DataTool.rpc_represent(result))
            return result

    class Service(IService):
        MAX_WORKERS: int = 10

        def __init__(self):
            self.description: ServiceDescription | None = None
            self.information: ServiceInformation | None = None
            self.subscribtions_map: dict[
                ServiceDescriptionBase, dict[SC, Subscribtion]
            ] = defaultdict(dict)
            self.server: Server | None = None

        def get_description(self) -> ServiceDescription:
            return self.description

        def serve(
            self,
            service_role_or_description: ServiceRoles | ServiceDescriptionBase,
            call_handler: Callable[[str, ParameterList, Any], Any] | None = None,
            starts_handler: Callable[[IService | None], None] | None = None,
            max_workers: int | None = None,
            depends_on_list: list[ServiceRoles | ServiceDescription] | None = None,
            as_standalone: bool = False,
            show_output: bool = True,
        ) -> None:
            if DEBUG:
                from pih import A
                from pih import PIHThreadPoolExecutor
            else:
                A = sys.modules["pih.pih"].A
                PIHThreadPoolExecutor = sys.modules["pih.pih"].PIHThreadPoolExecutor
            max_workers = max_workers or RPC.Service.MAX_WORKERS
            service_description: ServiceDescription = (
                service_role_or_description
                if isinstance(service_role_or_description, ServiceDescriptionBase)
                else ServiceRoleTool.service_description(service_role_or_description)
            )
            self.description = service_description
            with A.ER.detect():
                if not ServiceTool.is_service_as_listener(service_description):
                    A.SE.add_isolated_arg()
                    isolate_arg: str | None = None
                    try:
                        isolated_arg_value: str | None = A.SE.isolated_arg()
                        if nn(isolated_arg_value):
                            isolate_arg = str(isolated_arg_value).lower()
                    except AttributeError as error:
                        pass
                    if nn(isolate_arg):
                        if n(self.description.isolated):
                            self.description.isolated = isolate_arg not in [
                                "0",
                                "no",
                                "false",
                            ]
                        elif self.description.isolated:
                            self.description.isolated = isolate_arg not in [
                                "0",
                                "no",
                                "false",
                            ]
            #self.description.pih_version = self.description.pih_version or A.V.value
            self.description.host = ServiceAdminTool.create_host(self.description)
            self.description.port = ServiceAdminTool.create_port(self.description)
            self.information = DataTool.fill_data_from_source(
                ServiceInformation(standalone=as_standalone),
                self.description,
                skip_not_none=True,
            )
            self.information.pid = OSTool.pid()
            if e(RPC.service):
                RPC.service_description = self.description
                RPC.service_information = self.information
                RPC.service = self
            if show_output:
                A.O.init()
                A.O.service_header(self.information)
                A.O.good(f"Service was started!")
            self.server = grpc.server(
                PIHThreadPoolExecutor(max_workers=max_workers),
                options=GRPC_OPTIONS(),
                # compression=grpc.Compression.Gzip,
            )
            if n(RPC.server):
                RPC.server = self.server
            pb2_grpc.add_UnaryServicer_to_server(
                RPC.UnaryService(self, self.description, call_handler), self.server
            )
            try:
                if DEBUG:
                    from pih.tools import while_not_do
                else:
                    while_not_do = sys.modules["pih.pih"].while_not_do
                self.server.add_insecure_port(
                    ":".join((self.description.host, str(self.description.port)))
                )
                self.server.start()
                if ne(depends_on_list):
                    A.O.write_line("Dependencies availability check...")
                    while_not_do(
                        lambda: len(
                            list(
                                filter(
                                    lambda item: A.SRV.check_on_accessibility(
                                        item
                                        if isinstance(item, ServiceDescription)
                                        else item.value
                                    ),
                                    depends_on_list,
                                )
                            )
                        )
                        == len(depends_on_list)
                    )
                    A.O.write_line("All dependencies are online")
                RPC.SESSION.start_time = datetime.now().replace(second=0, microsecond=0)
                starts_handler(self)
                self.information.subscribtions = self.subscribtions
                RPC.call_service_command(SC.on_service_starts, self.information)
                with A.ER.detect_interruption("Выход"):
                    self.server.wait_for_termination()
            except RuntimeError as error:
                A.E.service_was_not_started(self.description, j(error.args))

        def create_subscribtions(
            self, information: ServiceDescriptionBase | None = None
        ) -> None:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A

            def internal_create_subscribtion(
                subscribtions: dict[ServiceDescriptionBase, dict[SC, Subscribtion]],
                information: ServiceDescriptionBase,
            ):
                for sc in subscribtions[information]:
                    subscription: Subscribtion = subscribtions[information][sc]
                    RPC.call_service(
                        information,
                        SC.subscribe,
                        (
                            DataTool.fill_data_from_source(
                                ServiceDescriptionBase(), self.information
                            ),
                            DataTool.fill_data_from_source(
                                SubscribtionInformation(), subscription
                            ),
                        ),
                    )
                    subscription.available = True
                    subscription.enabled = True

            for description_item in (
                self.subscribtions_map if e(information) else [information]
            ):
                if A.SRV.check_on_accessibility(description_item):
                    internal_create_subscribtion(
                        self.subscribtions_map, description_item
                    )

        @property
        def subscribtions(self) -> list[Subscribtion]:
            result: list[Subscribtion] = []
            for description_item in self.subscribtions_map:
                for sc in self.subscribtions_map[description_item]:
                    result.append(self.subscribtions_map[description_item][sc])
            return result

        def subscribe_on(
            self,
            sc: SC,
            type: int = SUBSCRIBTION_TYPE.ON_RESULT,
            name: str | None = None,
        ) -> bool:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A
            service_description: ServiceDescription = A.SRV.description_by_command(sc)
            if ne(service_description):
                if service_description != self.description:
                    subscribtion: Subscribtion | None = None
                    if sc not in self.subscribtions_map[service_description]:
                        subscribtion = Subscribtion(sc, type, name)
                        self.subscribtions_map[service_description][sc] = subscribtion
                    else:
                        subscribtion = self.subscribtions_map[service_description][sc]
                        subscribtion.type |= type
                    subscribtion.available = A.SRV.check_on_accessibility(
                        service_description
                    )
                    return subscribtion.available
            return False

        def unsubscribe(
            self, command_list: list[SC] | None = None, type: int | None = None
        ) -> None:
            if DEBUG:
                from pih import A
            else:
                A = sys.modules["pih.pih"].A
            for service_description in self.subscribtions_map:
                for sc in self.subscribtions_map[service_description]:
                    if sc in command_list:
                        DataTool.rpc_unrepresent(
                            RPC.call_service(
                                service_description, SC.unsubscribe, (self.description,)
                            )
                        )

        def unsubscribe_all(
            self, service_role_or_description: ServiceRoles | ServiceDescriptionBase
        ) -> bool:
            pass
            # return self.unsubscribe(service_role_or_description)

        def stop(self) -> None:
            self.server.stop(0)

    class CommandClient:
        def __init__(self, host: str, port: int):
            self.stub = pb2_grpc.UnaryStub(
                grpc.insecure_channel(
                    j((host, port), ":"),
                    options=GRPC_OPTIONS(),
                    # compression=grpc.Compression.Gzip,
                )
            )

        def call_command(
            self, name: str, parameters: str | None = None, timeout: int | None = None
        ):
            return self.stub.rpcCallCommand(
                pb2.rpcCommand(name=name, parameters=parameters), timeout=timeout
            )

    @staticmethod
    def ping(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> ServiceInformation | None:
        try:
            service_information: ServiceDescriptionBase = (
                ServiceRoleTool.service_description(service_role_or_description)
            )
            return DataTool.fill_data_from_rpc_str(
                ServiceInformation(),
                RPC.call_service(
                    service_information,
                    SC.ping,
                    ((RPC.service_information or STUB).name),
                ),
            )
        except Error:
            return None

    @staticmethod
    def stop(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> ServiceInformation:
        return RPC.call_service(
            ServiceRoleTool.service_description(service_role_or_description),
            SC.stop_service,
        )

    @staticmethod
    def check_availability(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase,
    ) -> bool:
        return ne(RPC.ping(service_role_or_description))

    @staticmethod
    def call_service(
        service_role_or_description: ServiceRoles | ServiceDescriptionBase | None,
        sc: SC,
        parameters: Any | None = None,
        timeout: int | None = None,
    ) -> str | None:
        if DEBUG:
            from pih import A
        else:
            A = sys.modules["pih.pih"].A
        information: ServiceDescriptionBase | None = (
            service_role_or_description
            if n(service_role_or_description)
            else ServiceRoleTool.service_description(service_role_or_description)
        )
        try:
            if e(information):
                information = A.SRV.description_by_command(sc)
            service_host: str | None = A.SRV.get_host(information)
            service_port: int | None = A.SRV.get_port(information)
            if e(timeout):
                if (
                    e(RPC.service_information)
                    or RPC.service_information.isolated
                    or information.isolated
                ):
                    if sc == SC.ping:
                        timeout = CONST_RPC.TIMEOUT_FOR_PING
                    else:
                        timeout = CONST_RPC.TIMEOUT
            return (
                RPC.CommandClient(service_host, service_port)
                .call_command(sc.name, DataTool.rpc_represent(parameters), timeout)
                .data
            )
        except grpc.RpcError as error:
            code: tuple = error.code()
            details: str = (
                f"Service role name: {information.name}\nHost: {service_host}:{service_port}\nCommand: {sc.name}\nDetails: {error.details()}\nCode: {code}"
            )
            A.O.init()
            A.ER.rpc_error_handler(details, code, information, sc, error.details())
            # raise Error(error.details(), code)

    @staticmethod
    def call_service_command(
        command: SC, parameters: Any | None = None, timeout: int | None = None
    ) -> str | None:
        return RPC.call_service(None, command, parameters, timeout)

    service: Service | None = None
    service_description: ServiceDescription | None = None
    service_information: ServiceInformation | None = None

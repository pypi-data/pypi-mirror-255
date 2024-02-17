# Copyright 2016 Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations

from .model import *


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    description: str = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class DumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> DumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DumpUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return DumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
        }


class CheckDumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CheckDumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckDumpUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckDumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckDumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
        }


class CleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CleanUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
        }


class CheckCleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CheckCleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckCleanUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckCleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckCleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
        }


class PrepareImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> PrepareImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareImportUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return PrepareImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
        }


class ImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> ImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> ImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ImportUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return ImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
        }


class CheckImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CheckImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> CheckImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckImportUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
        }


class DescribeEventMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeEventMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeEventMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeEventMastersRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeEventMastersRequest]:
        if data is None:
            return None
        return DescribeEventMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateEventMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    schedule_type: str = None
    absolute_begin: int = None
    absolute_end: int = None
    repeat_type: str = None
    repeat_begin_day_of_month: int = None
    repeat_end_day_of_month: int = None
    repeat_begin_day_of_week: str = None
    repeat_end_day_of_week: str = None
    repeat_begin_hour: int = None
    repeat_end_hour: int = None
    relative_trigger_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateEventMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateEventMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateEventMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateEventMasterRequest:
        self.metadata = metadata
        return self

    def with_schedule_type(self, schedule_type: str) -> CreateEventMasterRequest:
        self.schedule_type = schedule_type
        return self

    def with_absolute_begin(self, absolute_begin: int) -> CreateEventMasterRequest:
        self.absolute_begin = absolute_begin
        return self

    def with_absolute_end(self, absolute_end: int) -> CreateEventMasterRequest:
        self.absolute_end = absolute_end
        return self

    def with_repeat_type(self, repeat_type: str) -> CreateEventMasterRequest:
        self.repeat_type = repeat_type
        return self

    def with_repeat_begin_day_of_month(self, repeat_begin_day_of_month: int) -> CreateEventMasterRequest:
        self.repeat_begin_day_of_month = repeat_begin_day_of_month
        return self

    def with_repeat_end_day_of_month(self, repeat_end_day_of_month: int) -> CreateEventMasterRequest:
        self.repeat_end_day_of_month = repeat_end_day_of_month
        return self

    def with_repeat_begin_day_of_week(self, repeat_begin_day_of_week: str) -> CreateEventMasterRequest:
        self.repeat_begin_day_of_week = repeat_begin_day_of_week
        return self

    def with_repeat_end_day_of_week(self, repeat_end_day_of_week: str) -> CreateEventMasterRequest:
        self.repeat_end_day_of_week = repeat_end_day_of_week
        return self

    def with_repeat_begin_hour(self, repeat_begin_hour: int) -> CreateEventMasterRequest:
        self.repeat_begin_hour = repeat_begin_hour
        return self

    def with_repeat_end_hour(self, repeat_end_hour: int) -> CreateEventMasterRequest:
        self.repeat_end_hour = repeat_end_hour
        return self

    def with_relative_trigger_name(self, relative_trigger_name: str) -> CreateEventMasterRequest:
        self.relative_trigger_name = relative_trigger_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateEventMasterRequest]:
        if data is None:
            return None
        return CreateEventMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_schedule_type(data.get('scheduleType'))\
            .with_absolute_begin(data.get('absoluteBegin'))\
            .with_absolute_end(data.get('absoluteEnd'))\
            .with_repeat_type(data.get('repeatType'))\
            .with_repeat_begin_day_of_month(data.get('repeatBeginDayOfMonth'))\
            .with_repeat_end_day_of_month(data.get('repeatEndDayOfMonth'))\
            .with_repeat_begin_day_of_week(data.get('repeatBeginDayOfWeek'))\
            .with_repeat_end_day_of_week(data.get('repeatEndDayOfWeek'))\
            .with_repeat_begin_hour(data.get('repeatBeginHour'))\
            .with_repeat_end_hour(data.get('repeatEndHour'))\
            .with_relative_trigger_name(data.get('relativeTriggerName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "scheduleType": self.schedule_type,
            "absoluteBegin": self.absolute_begin,
            "absoluteEnd": self.absolute_end,
            "repeatType": self.repeat_type,
            "repeatBeginDayOfMonth": self.repeat_begin_day_of_month,
            "repeatEndDayOfMonth": self.repeat_end_day_of_month,
            "repeatBeginDayOfWeek": self.repeat_begin_day_of_week,
            "repeatEndDayOfWeek": self.repeat_end_day_of_week,
            "repeatBeginHour": self.repeat_begin_hour,
            "repeatEndHour": self.repeat_end_hour,
            "relativeTriggerName": self.relative_trigger_name,
        }


class GetEventMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    event_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetEventMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_event_name(self, event_name: str) -> GetEventMasterRequest:
        self.event_name = event_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventMasterRequest]:
        if data is None:
            return None
        return GetEventMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_event_name(data.get('eventName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "eventName": self.event_name,
        }


class UpdateEventMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    event_name: str = None
    description: str = None
    metadata: str = None
    schedule_type: str = None
    absolute_begin: int = None
    absolute_end: int = None
    repeat_type: str = None
    repeat_begin_day_of_month: int = None
    repeat_end_day_of_month: int = None
    repeat_begin_day_of_week: str = None
    repeat_end_day_of_week: str = None
    repeat_begin_hour: int = None
    repeat_end_hour: int = None
    relative_trigger_name: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateEventMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_event_name(self, event_name: str) -> UpdateEventMasterRequest:
        self.event_name = event_name
        return self

    def with_description(self, description: str) -> UpdateEventMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateEventMasterRequest:
        self.metadata = metadata
        return self

    def with_schedule_type(self, schedule_type: str) -> UpdateEventMasterRequest:
        self.schedule_type = schedule_type
        return self

    def with_absolute_begin(self, absolute_begin: int) -> UpdateEventMasterRequest:
        self.absolute_begin = absolute_begin
        return self

    def with_absolute_end(self, absolute_end: int) -> UpdateEventMasterRequest:
        self.absolute_end = absolute_end
        return self

    def with_repeat_type(self, repeat_type: str) -> UpdateEventMasterRequest:
        self.repeat_type = repeat_type
        return self

    def with_repeat_begin_day_of_month(self, repeat_begin_day_of_month: int) -> UpdateEventMasterRequest:
        self.repeat_begin_day_of_month = repeat_begin_day_of_month
        return self

    def with_repeat_end_day_of_month(self, repeat_end_day_of_month: int) -> UpdateEventMasterRequest:
        self.repeat_end_day_of_month = repeat_end_day_of_month
        return self

    def with_repeat_begin_day_of_week(self, repeat_begin_day_of_week: str) -> UpdateEventMasterRequest:
        self.repeat_begin_day_of_week = repeat_begin_day_of_week
        return self

    def with_repeat_end_day_of_week(self, repeat_end_day_of_week: str) -> UpdateEventMasterRequest:
        self.repeat_end_day_of_week = repeat_end_day_of_week
        return self

    def with_repeat_begin_hour(self, repeat_begin_hour: int) -> UpdateEventMasterRequest:
        self.repeat_begin_hour = repeat_begin_hour
        return self

    def with_repeat_end_hour(self, repeat_end_hour: int) -> UpdateEventMasterRequest:
        self.repeat_end_hour = repeat_end_hour
        return self

    def with_relative_trigger_name(self, relative_trigger_name: str) -> UpdateEventMasterRequest:
        self.relative_trigger_name = relative_trigger_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateEventMasterRequest]:
        if data is None:
            return None
        return UpdateEventMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_event_name(data.get('eventName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_schedule_type(data.get('scheduleType'))\
            .with_absolute_begin(data.get('absoluteBegin'))\
            .with_absolute_end(data.get('absoluteEnd'))\
            .with_repeat_type(data.get('repeatType'))\
            .with_repeat_begin_day_of_month(data.get('repeatBeginDayOfMonth'))\
            .with_repeat_end_day_of_month(data.get('repeatEndDayOfMonth'))\
            .with_repeat_begin_day_of_week(data.get('repeatBeginDayOfWeek'))\
            .with_repeat_end_day_of_week(data.get('repeatEndDayOfWeek'))\
            .with_repeat_begin_hour(data.get('repeatBeginHour'))\
            .with_repeat_end_hour(data.get('repeatEndHour'))\
            .with_relative_trigger_name(data.get('relativeTriggerName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "eventName": self.event_name,
            "description": self.description,
            "metadata": self.metadata,
            "scheduleType": self.schedule_type,
            "absoluteBegin": self.absolute_begin,
            "absoluteEnd": self.absolute_end,
            "repeatType": self.repeat_type,
            "repeatBeginDayOfMonth": self.repeat_begin_day_of_month,
            "repeatEndDayOfMonth": self.repeat_end_day_of_month,
            "repeatBeginDayOfWeek": self.repeat_begin_day_of_week,
            "repeatEndDayOfWeek": self.repeat_end_day_of_week,
            "repeatBeginHour": self.repeat_begin_hour,
            "repeatEndHour": self.repeat_end_hour,
            "relativeTriggerName": self.relative_trigger_name,
        }


class DeleteEventMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    event_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteEventMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_event_name(self, event_name: str) -> DeleteEventMasterRequest:
        self.event_name = event_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteEventMasterRequest]:
        if data is None:
            return None
        return DeleteEventMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_event_name(data.get('eventName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "eventName": self.event_name,
        }


class DescribeTriggersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTriggersRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeTriggersRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeTriggersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTriggersRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeTriggersRequest]:
        if data is None:
            return None
        return DescribeTriggersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeTriggersByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTriggersByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeTriggersByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeTriggersByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTriggersByUserIdRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeTriggersByUserIdRequest]:
        if data is None:
            return None
        return DescribeTriggersByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetTriggerRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    trigger_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetTriggerRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetTriggerRequest:
        self.access_token = access_token
        return self

    def with_trigger_name(self, trigger_name: str) -> GetTriggerRequest:
        self.trigger_name = trigger_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTriggerRequest]:
        if data is None:
            return None
        return GetTriggerRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_trigger_name(data.get('triggerName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "triggerName": self.trigger_name,
        }


class GetTriggerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    trigger_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetTriggerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetTriggerByUserIdRequest:
        self.user_id = user_id
        return self

    def with_trigger_name(self, trigger_name: str) -> GetTriggerByUserIdRequest:
        self.trigger_name = trigger_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTriggerByUserIdRequest]:
        if data is None:
            return None
        return GetTriggerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_trigger_name(data.get('triggerName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "triggerName": self.trigger_name,
        }


class TriggerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    trigger_name: str = None
    user_id: str = None
    trigger_strategy: str = None
    ttl: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> TriggerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_trigger_name(self, trigger_name: str) -> TriggerByUserIdRequest:
        self.trigger_name = trigger_name
        return self

    def with_user_id(self, user_id: str) -> TriggerByUserIdRequest:
        self.user_id = user_id
        return self

    def with_trigger_strategy(self, trigger_strategy: str) -> TriggerByUserIdRequest:
        self.trigger_strategy = trigger_strategy
        return self

    def with_ttl(self, ttl: int) -> TriggerByUserIdRequest:
        self.ttl = ttl
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> TriggerByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TriggerByUserIdRequest]:
        if data is None:
            return None
        return TriggerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_trigger_name(data.get('triggerName'))\
            .with_user_id(data.get('userId'))\
            .with_trigger_strategy(data.get('triggerStrategy'))\
            .with_ttl(data.get('ttl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "triggerName": self.trigger_name,
            "userId": self.user_id,
            "triggerStrategy": self.trigger_strategy,
            "ttl": self.ttl,
        }


class TriggerByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> TriggerByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> TriggerByStampSheetRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TriggerByStampSheetRequest]:
        if data is None:
            return None
        return TriggerByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DeleteTriggerRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    trigger_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTriggerRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteTriggerRequest:
        self.access_token = access_token
        return self

    def with_trigger_name(self, trigger_name: str) -> DeleteTriggerRequest:
        self.trigger_name = trigger_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteTriggerRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteTriggerRequest]:
        if data is None:
            return None
        return DeleteTriggerRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_trigger_name(data.get('triggerName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "triggerName": self.trigger_name,
        }


class DeleteTriggerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    trigger_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTriggerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteTriggerByUserIdRequest:
        self.user_id = user_id
        return self

    def with_trigger_name(self, trigger_name: str) -> DeleteTriggerByUserIdRequest:
        self.trigger_name = trigger_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteTriggerByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteTriggerByUserIdRequest]:
        if data is None:
            return None
        return DeleteTriggerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_trigger_name(data.get('triggerName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "triggerName": self.trigger_name,
        }


class DeleteTriggerByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DeleteTriggerByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DeleteTriggerByStampTaskRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteTriggerByStampTaskRequest]:
        if data is None:
            return None
        return DeleteTriggerByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeEventsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeEventsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeEventsRequest:
        self.access_token = access_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeEventsRequest]:
        if data is None:
            return None
        return DescribeEventsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class DescribeEventsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeEventsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeEventsByUserIdRequest:
        self.user_id = user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeEventsByUserIdRequest]:
        if data is None:
            return None
        return DescribeEventsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
        }


class DescribeRawEventsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRawEventsRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeRawEventsRequest]:
        if data is None:
            return None
        return DescribeRawEventsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetEventRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    event_name: str = None
    access_token: str = None
    is_in_schedule: bool = None

    def with_namespace_name(self, namespace_name: str) -> GetEventRequest:
        self.namespace_name = namespace_name
        return self

    def with_event_name(self, event_name: str) -> GetEventRequest:
        self.event_name = event_name
        return self

    def with_access_token(self, access_token: str) -> GetEventRequest:
        self.access_token = access_token
        return self

    def with_is_in_schedule(self, is_in_schedule: bool) -> GetEventRequest:
        self.is_in_schedule = is_in_schedule
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventRequest]:
        if data is None:
            return None
        return GetEventRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_event_name(data.get('eventName'))\
            .with_access_token(data.get('accessToken'))\
            .with_is_in_schedule(data.get('isInSchedule'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "eventName": self.event_name,
            "accessToken": self.access_token,
            "isInSchedule": self.is_in_schedule,
        }


class GetEventByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    event_name: str = None
    user_id: str = None
    is_in_schedule: bool = None

    def with_namespace_name(self, namespace_name: str) -> GetEventByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_event_name(self, event_name: str) -> GetEventByUserIdRequest:
        self.event_name = event_name
        return self

    def with_user_id(self, user_id: str) -> GetEventByUserIdRequest:
        self.user_id = user_id
        return self

    def with_is_in_schedule(self, is_in_schedule: bool) -> GetEventByUserIdRequest:
        self.is_in_schedule = is_in_schedule
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventByUserIdRequest]:
        if data is None:
            return None
        return GetEventByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_event_name(data.get('eventName'))\
            .with_user_id(data.get('userId'))\
            .with_is_in_schedule(data.get('isInSchedule'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "eventName": self.event_name,
            "userId": self.user_id,
            "isInSchedule": self.is_in_schedule,
        }


class GetRawEventRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    event_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRawEventRequest:
        self.namespace_name = namespace_name
        return self

    def with_event_name(self, event_name: str) -> GetRawEventRequest:
        self.event_name = event_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRawEventRequest]:
        if data is None:
            return None
        return GetRawEventRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_event_name(data.get('eventName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "eventName": self.event_name,
        }


class VerifyEventRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    event_name: str = None
    verify_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyEventRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyEventRequest:
        self.access_token = access_token
        return self

    def with_event_name(self, event_name: str) -> VerifyEventRequest:
        self.event_name = event_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyEventRequest:
        self.verify_type = verify_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyEventRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyEventRequest]:
        if data is None:
            return None
        return VerifyEventRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_event_name(data.get('eventName'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "eventName": self.event_name,
            "verifyType": self.verify_type,
        }


class VerifyEventByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    event_name: str = None
    verify_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyEventByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyEventByUserIdRequest:
        self.user_id = user_id
        return self

    def with_event_name(self, event_name: str) -> VerifyEventByUserIdRequest:
        self.event_name = event_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyEventByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyEventByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyEventByUserIdRequest]:
        if data is None:
            return None
        return VerifyEventByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_event_name(data.get('eventName'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "eventName": self.event_name,
            "verifyType": self.verify_type,
        }


class VerifyEventByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyEventByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyEventByStampTaskRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyEventByStampTaskRequest]:
        if data is None:
            return None
        return VerifyEventByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class ExportMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> ExportMasterRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExportMasterRequest]:
        if data is None:
            return None
        return ExportMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCurrentEventMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentEventMasterRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentEventMasterRequest]:
        if data is None:
            return None
        return GetCurrentEventMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentEventMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentEventMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentEventMasterRequest:
        self.settings = settings
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentEventMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentEventMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentEventMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentEventMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentEventMasterFromGitHubRequest:
        self.checkout_setting = checkout_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentEventMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentEventMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }
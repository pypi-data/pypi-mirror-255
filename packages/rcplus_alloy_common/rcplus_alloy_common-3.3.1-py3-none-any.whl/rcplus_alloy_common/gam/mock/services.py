
import copy
import string
import random
import sqlite3
from typing import Dict

import pandas as pd
from googleads.errors import GoogleAdsServerFault

from rcplus_alloy_common.gam.audience import AudienceSegmentStatus


DOC_URI = "https://developers.google.com/ad-manager/api/reference/v202308"


class MockCustomTargetingService:
    def __init__(self) -> None:
        # keys_cache and values_cache as tables in sqlite3
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            """
            CREATE TABLE keys (
                id INTEGER PRIMARY KEY,
                name TEXT,
                displayName TEXT,
                status TEXT,
                type TEXT,
                reportableType TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE key_values (
                id INTEGER PRIMARY KEY,
                name TEXT,
                displayName TEXT,
                matchType TEXT,
                status TEXT,
                customTargetingKeyId INTEGER
            )
            """
        )

    def __query__(self, query, params=None):
        return pd.read_sql(query, self.conn, params=params).to_dict("records")

    def __translate_statement__(self, statement, table="key_values", action: str = "SELECT"):
        if action == "SELECT":
            sql_query = f"SELECT * FROM {table} {statement['query']}"
        elif action == "DELETE":
            # NOTE: we don't support LIMIT
            sql_query = f"UPDATE {table} SET status='INACTIVE' {statement['query'].split('LIMIT')[0]}"
        else:
            raise NotImplementedError(f"Action {action} is not implemented")

        sql_params = {}
        if statement["values"]:
            for value in statement["values"]:
                if "value" in value["value"]:
                    sql_params[value["key"]] = value["value"]["value"]
                elif "values" in value["value"]:
                    new_param_binding = ""
                    for i, v in enumerate(value["value"]["values"]):
                        sql_params[f"{value['key']}_{i}"] = v["value"]
                        new_param_binding += f":{value['key']}_{i}, "

                    sql_query = sql_query.replace(f":{value['key']}", new_param_binding[:-2])
                else:
                    raise NotImplementedError(f"Value {value['value']} is not implemented")

        return sql_query, sql_params

    def __validate_createCustomTargetingKeys__(self, value):
        allowed_chars = set(" " + string.digits + string.ascii_letters + string.punctuation) - set(
            "\"'=!+#*~;^()<>[],"
        )
        if "customTargetingKeyId" not in value:
            error = {
                "fieldPath": "customTargetingKeyId",
                "fieldPathElements": [{"field": "customTargetingKeyId", "index": None}],
                "trigger": value["customTargetingKeyId"],
                "errorString": "CustomTargetingError.KEY_NAME_EMPTY",
                "reason": "KEY_NAME_EMPTY",
            }
        elif len(self.__query__("SELECT id FROM keys WHERE id = ?", params=(value["customTargetingKeyId"],))) == 0:
            error = {
                "fieldPath": "customTargetingKeyId",
                "fieldPathElements": [{"field": "customTargetingKeyId", "index": None}],
                "trigger": value["customTargetingKeyId"],
                "errorString": "CustomTargetingError.KEY_NOT_FOUND",
                "reason": "KEY_NOT_FOUND",
            }
        elif "name" not in value:
            error = {
                "fieldPath": "name",
                "fieldPathElements": [{"field": "name", "index": None}],
                "trigger": value["name"],
                "errorString": "CustomTargetingError.VALUE_NAME_EMPTY",
                "reason": "VALUE_NAME_EMPTY",
            }
        elif len(value["name"]) > 40:
            error = {
                "fieldPath": "name",
                "fieldPathElements": [{"field": "name", "index": None}],
                "trigger": value["name"],
                "errorString": "CustomTargetingError.VALUE_NAME_INVALID_LENGTH",
                "reason": "VALUE_NAME_INVALID_LENGTH",
            }
        elif not all(char in allowed_chars for char in value["name"]):
            error = {
                "fieldPath": "name",
                "fieldPathElements": [{"field": "name", "index": None}],
                "trigger": value["name"],
                "errorString": "CustomTargetingError.VALUE_NAME_INVALID_CHARS",
                "reason": "VALUE_NAME_INVALID_CHARS",
            }
        elif len(self.__query__("SELECT id FROM key_values WHERE name = ?", params=(value["name"],))) > 0:
            error = {
                "fieldPath": "name",
                "fieldPathElements": [{"field": "name", "index": None}],
                "trigger": value["name"],
                "errorString": "CustomTargetingError.VALUE_NAME_DUPLICATE",
                "reason": "VALUE_NAME_DUPLICATE",
            }
        else:
            error = None
        return error

    def getCustomTargetingKeysByStatement(self, statement):
        sql_query, sql_params = self.__translate_statement__(statement, table="keys", action="SELECT")
        results = self.__query__(sql_query, params=sql_params)
        return {
            "totalResultSetSize": len(results),
            "startIndex": 0,
            "results": results,
        }

    def createCustomTargetingKeys(self, keys):
        """

        we support a (small) subset of the possible errors

        Raises:
            googleads.errors.GoogleAdsServerFault:
                CustomTargetingError.KEY_NAME_DUPLICATE: CustomTargetingKey with the same CustomTargetingKey.name
                    already exists.
                CustomTargetingError.KEY_NAME_EMPTY: CustomTargetingKey.name is empty.
                CustomTargetingError.KEY_NAME_INVALID_LENGTH: CustomTargetingKey.name is too long.
                CustomTargetingError.KEY_NAME_INVALID_CHARS: CustomTargetingKey.name contains unsupported or reserved
                    characters.
        """
        keys = copy.deepcopy(keys)
        errors = []
        for key in keys:
            if "name" not in key:
                errors.append(
                    {
                        "fieldPath": "name",
                        "fieldPathElements": [{"field": "name", "index": None}],
                        "trigger": key["name"],
                        "errorString": "CustomTargetingError.KEY_NAME_EMPTY",
                        "reason": "KEY_NAME_EMPTY",
                    }
                )
                continue
            if len(key["name"]) > 10:
                errors.append(
                    {
                        "fieldPath": "name",
                        "fieldPathElements": [{"field": "name", "index": None}],
                        "trigger": key["name"],
                        "errorString": "CustomTargetingError.KEY_NAME_INVALID_LENGTH",
                        "reason": "KEY_NAME_INVALID_LENGTH",
                    }
                )
                continue
            allowed_chars = set(string.digits + string.ascii_letters + string.punctuation) - set("\"'=!+#*~;^()<>[], ")
            if not all(char in allowed_chars for char in key["name"]):
                errors.append(
                    {
                        "fieldPath": "name",
                        "fieldPathElements": [{"field": "name", "index": None}],
                        "trigger": key["name"],
                        "errorString": "CustomTargetingError.KEY_NAME_INVALID_CHARS",
                        "reason": "KEY_NAME_INVALID_CHARS",
                    }
                )
                continue
            if len(self.__query__("SELECT * FROM keys WHERE name = ?", params=(key["name"],))):
                errors.append(
                    {
                        "fieldPath": "name",
                        "fieldPathElements": [{"field": "name", "index": None}],
                        "trigger": key["name"],
                        "errorString": "CustomTargetingError.KEY_NAME_DUPLICATE",
                        "reason": "KEY_NAME_DUPLICATE",
                    }
                )
                continue

            key["id"] = random.choice(range(100000000, 999999999))
            key["status"] = "ACTIVE"
            key["name"] = key["name"].lower()  # TODO: this assumption has to be checked
            if "reportableType" not in key:
                key["reportableType"] = "UNKNOWN"

            self.conn.execute(
                "INSERT INTO keys (id, name, displayName, status, type, reportableType) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    key["id"],
                    key["name"],
                    key["displayName"],
                    key["status"],
                    key["type"],
                    key["reportableType"],
                ),
            )

        if errors:
            # NOTE: the schema might be different
            raise GoogleAdsServerFault(
                document=f"{DOC_URI}/CustomTargetingService.CustomTargetingError",
                errors=errors,
                message=[f"{error['errorString']} @ name: {error['trigger']}" for error in errors],
            )
        return keys

    def createCustomTargetingValues(self, values):
        """

        we support a (small) subset of the possible errors

        Raises:
            googleads.errors.GoogleAdsServerFault:
                CustomTargetingError.KEY_NAME_EMPTY: CustomTargetingKey.name is empty.
                CustomTargetingError.KEY_NOT_FOUND: Requested CustomTargetingKey is not found.
                CustomTargetingError.VALUE_NAME_EMPTY: CustomTargetingValue.name is empty.
                CustomTargetingError.VALUE_NAME_INVALID_LENGTH: CustomTargetingValue.name is too long.
                CustomTargetingError.VALUE_NAME_INVALID_CHARSCustomTargetingValue.name contains unsupported or reserved
                    characters.
                CustomTargetingError.VALUE_NAME_DUPLICATE: CustomTargetingValue with the same CustomTargetingValue.name
                    already exists.
        """
        errors = []
        response = []
        values = copy.deepcopy(values)
        for value in values:
            error = self.__validate_createCustomTargetingKeys__(value)
            if error:
                errors.append(error)
                continue
            value["id"] = random.choice(range(100000000, 999999999))
            value["status"] = "ACTIVE"
            # NOTE: you can create it with upper case, but it will be converted to lower case
            value["name"] = value["name"].lower()
            if "matchType" not in value:
                value["matchType"] = "EXACT"
            if "displayName" not in value:
                value["displayName"] = value["name"]
            response.append(value)
            self.conn.execute(
                """
                    INSERT INTO key_values
                    (id, name, displayName, matchType, status, customTargetingKeyId)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    value["id"],
                    value["name"],
                    value["displayName"],
                    value["matchType"],
                    value["status"],
                    value["customTargetingKeyId"],
                ),
            )
        if errors:
            # NOTE: the schema might be different
            raise GoogleAdsServerFault(
                document=f"{DOC_URI}/CustomTargetingService.CustomTargetingError",
                errors=errors,
                message=[f"{error['errorString']} @ name: {error['trigger']}" for error in errors],
            )
        return response

    def updateCustomTargetingValues(self, values):
        """

        Raises:
            googleads.errors.GoogleAdsServerFault:
                CustomTargetingError.VALUE_NOT_FOUND: Requested CustomTargetingValue is not found.

        """
        response = []
        errors = []
        values = copy.deepcopy(values)
        for value in values:
            if len(self.__query__("SELECT id FROM key_values WHERE id = ?", params=(value["id"],))) == 0:
                errors.append(
                    {
                        "fieldPath": "id",
                        "fieldPathElements": [{"field": "id", "index": None}],
                        "trigger": value["id"],
                        "errorString": "CustomTargetingError.VALUE_NOT_FOUND",
                        "reason": "VALUE_NOT_FOUND",
                    }
                )
                continue

            for _key, _value in value.items():
                if _key == "id":
                    continue
                self.conn.execute(
                    f"UPDATE key_values SET {_key} = ? WHERE id = ?",
                    (
                        _value,
                        value["id"],
                    ),
                )
            new_value = self.__query__("SELECT * FROM key_values WHERE id = ?", params=(value["id"],))[0]
            response.append(new_value)
        if errors:
            # NOTE: the schema might be different
            raise GoogleAdsServerFault(
                document=f"{DOC_URI}/CustomTargetingService.CustomTargetingError",
                errors=errors,
                message=[f"ValueError.CUSTOM_TARGETING_VALUE_ID_NOT_FOUND @ id: {value['id']}" for value in values],
            )
        return response

    def getCustomTargetingValuesByStatement(self, statement):
        sql_query, sql_params = self.__translate_statement__(statement, table="key_values", action="SELECT")
        results = self.__query__(sql_query, params=sql_params)
        return {
            "totalResultSetSize": len(results),
            "startIndex": 0,
            "results": results,
        }

    def performCustomTargetingValueAction(self, action, statement):
        if action["xsi_type"] != "DeleteCustomTargetingValues":
            raise NotImplementedError()

        sql_query, sql_params = self.__translate_statement__(statement, table="key_values", action="DELETE")
        results = self.conn.execute(sql_query, sql_params)
        return {
            "numChanges": results.rowcount,
        }

    def performCustomTargetingKeyAction(self, action, statement):
        if action != {"xsi_type": "DeleteCustomTargetingKeys"}:
            raise NotImplementedError()

        sql_query, sql_params = self.__translate_statement__(statement, table="keys", action="DELETE")
        results = self.conn.execute(sql_query, sql_params)
        return {
            "numChanges": results.rowcount,
        }


class MockNetworkService:
    def makeTestNetwork(self, *args, **kwargs):  # pylint: disable=unused-argument
        return {"networkCode": "test_network"}

    def getAllNetworks(self, *args, **kwargs):  # pylint: disable=unused-argument
        return [
            {"networkCode": "prod_network", "isTest": False},
        ]


class MockAudienceSegmentService:
    def __init__(self) -> None:
        self.segments_cache: Dict = {}

    def createAudienceSegments(self, segments):
        response = []
        segments = copy.deepcopy(segments)
        for segment in segments:
            doc = {
                "id": random.choice(range(100000000, 999999999)),
                "name": segment["name"],
                "status": AudienceSegmentStatus.ACTIVE,
                "type": "FIRST_PARTY",
                "membershipExpirationDays": int(segment["membershipExpirationDays"]),
            }
            if "description" in segment:
                doc["description"] = segment["description"]
            response.append(doc)
            self.segments_cache[doc["id"]] = doc
        return response

    def updateAudienceSegments(self, segments):
        response = []
        errors = []
        segments = copy.deepcopy(segments)
        for segment in segments:
            if segment["id"] not in self.segments_cache:
                errors.append(
                    {
                        "fieldPath": "id",
                        "fieldPathElements": [{"field": "id", "index": None}],
                        "trigger": segment["id"],
                        "errorString": "SegmentError.AUDIENCE_SEGMENT_ID_NOT_FOUND",
                        "reason": "AUDIENCE_SEGMENT_ID_NOT_FOUND",
                    }
                )
                continue

            for key, value in segment.items():
                if key == "id":
                    continue
                self.segments_cache[segment["id"]][key] = value if key != "membershipExpirationDays" else int(value)
            response.append(self.segments_cache[segment["id"]])
        if errors:
            # NOTE: the schema might be different
            raise GoogleAdsServerFault(
                document=f"{DOC_URI}/AudienceSegmentService.AudienceSegmentError",
                errors=errors,
                message=[
                    f"AudienceSegmentError.AUDIENCE_SEGMENT_ID_NOT_FOUND @ id: {segment['id']}" for segment in segments
                ],
            )
        return response

    def getAudienceSegmentsByStatement(self, statement):
        # we mock just search by id, otherwise we raise NotImplementedError
        if "id" not in statement["query"]:
            raise NotImplementedError("Only search by id is mocked")
        segment_id = statement["query"].split("id = ")[1].split(" ")[0]
        if segment_id.strip().startswith(":"):
            for value in statement["values"]:
                if value["key"] == "id":
                    segment_id = value["value"]["value"]
                    break
        if segment_id in self.segments_cache:
            return {
                "totalResultSetSize": 1,
                "startIndex": 0,
                "results": [
                    copy.deepcopy(self.segments_cache[segment_id]),
                ],
            }

        return {
            "totalResultSetSize": 0,
            "startIndex": 0,
            "results": [],
        }

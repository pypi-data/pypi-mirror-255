import logging
from typing import TypedDict, List, Optional

import googleads

from ..logging import change_logging_level
from .utils import GoogleServiceAccountClient
from .constants import DISPLAY_NAME_PREFIX
from .network import Network


logger = logging.getLogger(__name__)


class BaseValue(TypedDict):
    name: str
    displayName: str  # noqa: N815
    matchType: str  # noqa: N815


class Value(BaseValue):
    """Value type definition"""
    id: Optional[str]
    customTargetingKeyId: str  # noqa: N815


class KeyValues:
    """KeyValues class to manage GAM key-values"""
    def __init__(
        self,
        key_name: str,
        key_display_name: str,
        application_name: str,
        env_tag: str,
        gcp_key: dict,
        version: str = "v202302",
        **kwargs,
    ) -> None:
        self.version = version
        network = Network(application_name=application_name, env_tag=env_tag, gcp_key=gcp_key, **kwargs)
        oauth2_client = GoogleServiceAccountClient(gcp_key, googleads.oauth2.GetAPIScope("ad_manager"))
        ad_manager_client = googleads.ad_manager.AdManagerClient(
            oauth2_client,
            application_name=application_name,
            network_code=network.network_code,
            **kwargs,
        )
        self.custom_targeting_service = ad_manager_client.GetService("CustomTargetingService", version=self.version)
        if env_tag == "prod":
            self.key_name = key_name
        else:
            self.key_name = f"{key_name}_{env_tag}"
        self.key_display_name = f"{DISPLAY_NAME_PREFIX} - {key_display_name}"
        self.key = self.__get_key__()
        logger.info(f"Use GAM key ID: {self.key['id']} {self.key['name']} `{self.key['displayName']}`.")

    def __get_key__(self):
        key_statement = (
            googleads.ad_manager.StatementBuilder(version=self.version)
            .Where("name = :name")
            .WithBindVariable("name", self.key_name)
        )
        response = self.custom_targeting_service.getCustomTargetingKeysByStatement(key_statement.ToStatement())
        if "results" in response and len(response["results"]):
            # The results could also include an INACTIVE key
            return response["results"][0]
        return self.__create_key__()

    def __create_key__(self):
        return self.custom_targeting_service.createCustomTargetingKeys(
            [
                {
                    "name": self.key_name,
                    "displayName": self.key_display_name,
                    "type": "PREDEFINED",
                }
            ]
        )[0]

    def insert_value(self, value_name, value_display_name, value_match_type="EXACT"):
        value = [
            Value(
                id=None,
                name=value_name,
                displayName=value_display_name,
                matchType=value_match_type,
                customTargetingKeyId=self.key["id"],
            )
        ]
        response = self.custom_targeting_service.createCustomTargetingValues(value)
        logger.info(f"Added new value ID {value_name} `{value_display_name}`")
        return response[0]

    def insert_values(self, values: List[BaseValue]):
        new_values: List[Value] = []
        for value in values:
            new_values.append(
                Value(
                    id=None,
                    name=value["name"],
                    displayName=value["displayName"],
                    matchType=value["matchType"],
                    customTargetingKeyId=self.key["id"],
                )
            )

        response = self.custom_targeting_service.createCustomTargetingValues(new_values)
        logger.info(f"Added {len(response)} values")
        return response

    def update_value(self, value_id, value_name, value_display_name, value_match_type="EXACT"):
        value = [
            Value(
                id=value_id,
                name=value_name,
                displayName=value_display_name,
                matchType=value_match_type,
                customTargetingKeyId=self.key["id"],
            )
        ]
        response = self.custom_targeting_service.updateCustomTargetingValues(value)
        logger.info(f"Updated value ID {value_name} `{value_display_name}`")
        return response[0]

    def delete_values(self, values: List[BaseValue] | None = None):
        key_id = self.key["id"]

        if not values:
            values_filter_statement = (
                googleads.ad_manager.StatementBuilder(version=self.version)
                .Where("customTargetingKeyId = :keyId AND status = :status")
                .WithBindVariable("keyId", key_id)
                .WithBindVariable("status", "ACTIVE")
            )
        else:
            values_filter_statement = (
                googleads.ad_manager.StatementBuilder(version=self.version)
                .Where("customTargetingKeyId = :keyId AND displayName IN (:names) AND status = :status")
                .WithBindVariable("keyId", key_id)
                .WithBindVariable("names", [value["displayName"] for value in values])
                .WithBindVariable("status", "ACTIVE")
            )

        while True:
            # Get custom targeting values.
            response = self.custom_targeting_service.getCustomTargetingValuesByStatement(
                values_filter_statement.ToStatement()
            )

            if not response["results"]:
                break
            _values = response["results"]
            total_values = response["totalResultSetSize"]
            logger.info(f"Total number of custom targeting values is {total_values}")
            logger.info(f"Number of custom targeting values to be deleted: {len(_values)}")
            action = {"xsi_type": "DeleteCustomTargetingValues"}
            filter_statement = (
                googleads.ad_manager.StatementBuilder(version=self.version)
                .Where("customTargetingKeyId = :keyId AND id IN (:ids)")
                .WithBindVariable("keyId", key_id)
                .WithBindVariable("ids", [value["id"] for value in _values])
            )

            # Delete custom targeting values.
            result = self.custom_targeting_service.performCustomTargetingValueAction(
                action, filter_statement.ToStatement()
            )

            # Display results.
            if result and result["numChanges"] > 0:
                logger.info(f"Number of custom targeting values deleted: {result['numChanges']}")
            else:
                logger.info("No custom targeting values were deleted.")

    def delete(self):
        self.delete_values()
        action = {"xsi_type": "DeleteCustomTargetingKeys"}
        key_statement = (
            googleads.ad_manager.StatementBuilder(version=self.version).Where(f"id = {self.key['id']}")
        )
        result = self.custom_targeting_service.performCustomTargetingKeyAction(action, key_statement.ToStatement())
        return result

    def upsert_values(self, values: List[BaseValue]):
        """upsert_values

        NOTE: ideally values should contain just values which needs to be updated or added
        TODO: deactivate values

        NOTE: Add new values one by one because new values can be added for the existing GAM key (among already existing
        values) and if all the values added all at once they would fail all at once because of data conflicts.
        """
        new_values: List[Value] = []
        updated_values = []
        for base_value in values:
            value = Value(
                id=None,
                name=base_value["name"],
                displayName=base_value["displayName"],
                matchType=base_value["matchType"],
                customTargetingKeyId=self.key["id"],
            )

            try:
                with change_logging_level(logging.getLogger("googleads.soap"), log_level=logging.ERROR):
                    response = self.insert_value(value["name"], value["displayName"])
                new_values.append(response)
            except googleads.errors.GoogleAdsServerFault as ex:
                error = str(ex)
                if "VALUE_NAME_DUPLICATE" not in error:
                    raise

                # logger.debug(f"Value ID {value["name"]} already exists")
                existing_value: Value = self.custom_targeting_service.getCustomTargetingValuesByStatement(
                    googleads.ad_manager.StatementBuilder(version=self.version)
                    .Where("name = :name AND customTargetingKeyId = :key_id")
                    .WithBindVariable("name", value["name"])
                    .WithBindVariable("key_id", self.key["id"])
                    .ToStatement()
                )["results"][0]
                if existing_value["displayName"] != value["displayName"]:
                    response = self.update_value(
                        existing_value["id"],
                        value["name"],
                        value["displayName"]
                    )
                    updated_values.append(response)
                else:
                    logger.info(
                        "No change detected. skip updating value "
                        f"{value['name']} `{value['displayName']}`"
                    )

        if not new_values:
            logger.info("No new values were added")
        else:
            logger.info(f"{len(new_values)} new values were added")

    def get_values(self, active: bool = True, search_filter: str | None = None):
        all_values = []
        key_id = self.key["id"]
        query = f"customTargetingKeyId={key_id}"
        if search_filter:
            query += f" AND displayName LIKE '%{search_filter}%'"
        if active:
            query += " AND status='ACTIVE'"
        statement = googleads.ad_manager.StatementBuilder(version=self.version).Where(query)

        while True:
            response = self.custom_targeting_service.getCustomTargetingValuesByStatement(statement.ToStatement())
            if "results" in response and len(response["results"]):
                all_values.extend(response["results"])
                statement.offset += statement.limit
                continue
            break

        return all_values

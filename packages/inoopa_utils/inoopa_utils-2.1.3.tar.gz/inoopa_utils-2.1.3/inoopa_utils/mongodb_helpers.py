from dotenv import load_dotenv
load_dotenv()

import os
from copy import deepcopy
from typing import Literal
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient, UpdateOne, ASCENDING, TEXT

from inoopa_utils.inoopa_logging import create_logger
from inoopa_utils.custom_types.websites import CompanyWebsiteContent
from inoopa_utils.custom_types.companies import Company, Establishment, convert_dict_to_company

class DbManagerMongo:
    """
    This class is used to manage the Mongo database (InfraV2).
    
    :param mongo_uri: The URI of the Mongo database to connect to.
    
    :method update_or_add_one_to_collection: Update or add a company or a website content to the database.
    :method add_or_update_many_to_collection: Update or add a list of companies or website contents to the database.
    :method find_one_from_collection: Get a company or a website content from the database.
    :method find_many_from_collection: Get a list of companies or website contents from the database.
    :method delete_one_from_collection: Delete a company or a website content from the database.
    """
    def __init__(self, mongo_uri: str = os.environ["MONGO_READWRITE_PROD_URI"]):
        self._logger = create_logger("INOOPA_UTILS.DB_MANAGER.MONGO")
        self._env = os.environ.get("ENV", "dev")

        _client = MongoClient(mongo_uri)
        _db = _client[self._env]

        self.company_collection = _db.get_collection("company")
        self.website_content_collection = _db.get_collection("website_content")
        self.do_not_call_me_collection = _db.get_collection("do_not_call_me")
        self.decision_maker_collection = _db.get_collection("decision_maker")
        # Ensure all indexes are created
        fields_to_index_company = [
            [("address.string_address", ASCENDING)],
            [("best_website", ASCENDING)],
            [("best_email", ASCENDING)],
            [("best_phone", ASCENDING)],
            [("board_members.name", ASCENDING)],
            [("country", ASCENDING)],
            [("employee_category_code", ASCENDING)],
            [("establishments.name", ASCENDING)],
            [("name", ASCENDING)],
            [("status", ASCENDING)],
            [("name_text", TEXT)],
        ]
        fields_to_index_decision_makers = [
            [("company_id", ASCENDING)],
            [("email_score", ASCENDING)],
            [("phone_score", ASCENDING)],
            [("function_code", ASCENDING)],
            [("cluster", ASCENDING)],
            [("cluster_score", ASCENDING)],
            [("cluster_best_match", ASCENDING)],
            [("function_string", ASCENDING)],
        ]
        self._logger.info("Creating indexes in collections (if not created yet)...")
        self._logger.info(
            "If this takes time (~10 mins), the indexes are not created yet. You will get a message when it's done."
        )
        for index in fields_to_index_company:
            self._logger.debug(f"Creating index {index} in `company` collection...")
            self.company_collection.create_index(index, background=True)
        for index in fields_to_index_decision_makers:
            self._logger.debug(f"Creating index {index} in `decision_maker` collection...")
            self.decision_maker_collection.create_index(index, background=True)
        self._logger.debug("Creating index in `do_not_call_me` collection...")
        self.do_not_call_me_collection.create_index([("phone", ASCENDING)], unique=True, background=True)
        self._logger.info("Indexes created in all collections")


    def update_or_add_one_to_collection(self, data: Company) -> None:
        """
        Update or add a company or a website content to the database.
        
        :param data: The company or website content to add or update.
        """
        if isinstance(data, Company):
            data_found = self.company_collection.find_one({"_id": data._id})
            if data_found:
                # Update only the fields that needs to be updated
                data = _update_entity_object(data, convert_dict_to_company(data_found))
            else:
                # Remove the _id field to avoid error
                data = asdict(data)
            
            self.company_collection.update_one(
                filter={"_id": data._id},
                update={"$set": data},
                upsert=True,
            )
            self._logger.info(f"Updated/created Company in collection {self._env} with _id: {data._id}")
        
        elif isinstance(data, CompanyWebsiteContent):
            self.website_content_collection.update_one(
                filter={"url": data.url},
                update={"$set": asdict(data)},
                upsert=True,
            )
            self._logger.info(f"Updated WebsiteContent in collection {self._env} with url: {data.url}")
        else:
            raise TypeError(f"Can't update or add data to mongo. Type {type(data)} is not supported.")

    def update_or_add_many_to_collection(self, data_list: list[Company | CompanyWebsiteContent]) -> None:
        """
        Update or add a list of companies or website contents to the database.
        
        :param data: The list of companies or website contents to add or update.
        """
        if not data_list:
            self._logger.warning("Didn't find any company to send to DB!")
            return
        
        self._logger.info(f"Sending {len(data_list)} entities to DB...")
        if all(isinstance(x, Company) for x in data_list):
            # Get the companies already in the database
            self._logger.info("try to fetch companies already in DB...")
            in_db_companies = self.find_many_companies([x._id for x in data_list], "inoopa_id")
            # Convert the list to a dict for faster access
            db_companies_dict = {x._id: x for x in in_db_companies}
            # Update the companies with the new data
            self._logger.info("Merge new companies data with companies in DB...")
            updated_companies = [_update_entity_object(company, db_companies_dict.get(company._id)) for company in data_list]
            # prepare the operations to do in the database for faster query
            updates = [UpdateOne({"_id": x._id}, {"$set": asdict(x)}, upsert=True) for x in updated_companies]
            # Do the bulk update
            self._logger.info(f"Writing {len(updates)} companies to DB...")
            query_result = self.company_collection.bulk_write(updates)
            self._logger.info(f"Updated: {query_result.modified_count} | Inserted: {query_result.inserted_count} | Upserted: {query_result.upserted_count}  Companies in collection {self._env}")
        
        elif all(isinstance(x, CompanyWebsiteContent) for x in data_list):
            self._logger.info("try to fetch website content already in DB...")
            updates = [UpdateOne({"url": x.url}, {"$set": asdict(x)}, upsert=True) for x in data_list]
            self._logger.info(f"Writing {len(updates)} websites content to DB...")
            query_result = self.website_content_collection.bulk_write(updates)
            self._logger.info(f"Updated {query_result.modified_count} | Inserted: {query_result.inserted_count} | Upserted: {query_result.upserted_count} |  WebsiteContent in collection {self._env} with urls: {[x.url for x in data_list]}")
        else:
            raise TypeError(f"Can't update or add many data to mongo. Probably a mix of types in the list.")

    def find_one_company(self, id: str, id_type: Literal["company_number", "inoopa_id"] = "company_number") -> Company | None:
        """
        Get a list of companies from the database based on ids.
        
        :param id: company id to get.
        :return: The company if found, None otherwise.
        """
        
        if id_type == "company_number":
            data_found = self.company_collection.find_one({"company_number": id})
        elif id_type == "inoopa_id":
            data_found = self.company_collection.find_one({"_id": id})
        else:
            raise TypeError(f"id_type {id_type} is not supported. Use company_number or inoopa_id.")
        return convert_dict_to_company(data_found) if data_found else None

    def find_many_companies(self, ids = list[str], id_type: Literal["company_number", "inoopa_id"] = "inoopa_id") -> list[Company] | None:
        """
        Get a list of companies from the database based on ids.
        
        :param ids: The list of companies ids to get.
        :return: The list of companies if found, None otherwise.
        """
        if type(ids) not in [list]:
            raise TypeError(f"You ids list is not a list. Type {type(ids)} is not supported.")
        
        if id_type == "company_number":
            data_found = self.company_collection.find({"company_number": {"$in": ids}})

        elif id_type == "inoopa_id":
            data_found = self.company_collection.find({"_id": {"$in": ids}})
        else:
            raise TypeError(f"id_type {id_type} is not supported. Use company_number or inoopa_id.")
        return [convert_dict_to_company(x) for x in data_found] if data_found else None

    def delete_one_from_collection(self, data: Company | CompanyWebsiteContent) -> None:
        """
        Delete a company or a website content from the database.
        
        :param data: The company or website content to delete.
        """
        
        if isinstance(data, Company):
            self.company_collection.delete_one({"_id": data._id})
            self._logger.info(f"Deleted Company from collection {self._env} with ID: {data._id}")
        
        elif isinstance(data, CompanyWebsiteContent):
            self.company_collection.delete_one({"url": data.url})
            self._logger.info(f"Deleted WebsiteContent from collection {self._env} with url: {data.url}")
        else:
            raise TypeError(f"Can't update or add data to mongo. Type {type(data)} is not supported.")

    def delete_many_from_collection(self, data_list: list[Company | CompanyWebsiteContent]) -> None:
        """
        Delete a list of companies or website contents from the database.
        
        :param data: The list of companies or website contents to delete.
        """
        if all(isinstance(x, Company) for x in data_list):
            all_ids = [x._id for x in data_list]
            self.company_collection.delete_many({"_id": {"$in": all_ids}})
            self._logger.info(f"Deleted Companies from collection {self._env} with IDs: {all_ids}")

        elif all(isinstance(x, CompanyWebsiteContent) for x in data_list):
            all_ids = [x.url for x in data_list]
            self.website_content_collection.delete_many({"url": {"$in": all_ids}})
            self._logger.info(f"Deleted WebsiteContent from collection {self._env} with url: {all_ids}")
        else:
            raise TypeError(f"Can't update or add many data to mongo. Probably a mix of types in the list.")

    def update_do_not_call_me(self, phones: list[str]) -> None:
        """
        Method to update the do_not_call_me collection in the database.

        :param list[str]: The list of phone numbers to add to the do_not_call_me collection.
        """
        batch_size = 10_000
        phones_batch = [phones[i:i + batch_size] for i in range(0, len(phones), batch_size)]

        # We use a thread pool to update the database faster
        with ThreadPoolExecutor() as executor:
            executor.map(self._run_batch_update_do_not_call_me, phones_batch)
        self._logger.info(f"Updated {len(phones):_} phones in DoNotCallMe collection")

    def _run_batch_update_do_not_call_me(self, phone_batch: list[str]) -> None:
        """
        Method to update a chunk of the do_not_call_me collection in the database.

        :param updates: The list of DB update to execute.
        """
        batch_set = set(phone_batch)
        self._logger.info(f"Filtering {len(phone_batch)} phones...")
        existing_numbers = set(item['phone'] for item in self.do_not_call_me_collection.find({"phone": {"$in": list(batch_set)}}))
        new_numbers = [{"phone": number} for number in batch_set - existing_numbers]
        # Bulk insert new numbers
        if new_numbers:
            self._logger.info(f"Inserting {len(new_numbers)} new phones in collection...")
            self.do_not_call_me_collection.insert_many(new_numbers, ordered=False)
        else:
            self._logger.info(f"No new phones to insert found in batch")

# ------- Helpers -------
def _update_entity_object(new_entity_data: Company | Establishment | None, db_entity_data: Company | None) -> Company | Establishment | None:
    """
    Compare the new entity (a company or an establishment) data with the one in the database and update the required fields.

    :param new_entity_data: The entity with the new data.
    :param db_entity_data: The entity with the data from the database.
    """
    if db_entity_data is None or new_entity_data is None:
        return new_entity_data

    # TODO: When NACE codes correction is implemented, handle it here
    append_fields = ["addresses", "emails", "phones", "websites", "social_networks"]
    to_skip_fields = ["establishments", "_id"]
    
    db_entity_data_dict = asdict(db_entity_data)
    new_entity_data_dict = asdict(new_entity_data)

    for key in new_entity_data_dict.keys():
        if new_entity_data_dict[key] is None or key in to_skip_fields:
            continue

        if key not in append_fields:
            db_entity_data_dict[key] = new_entity_data_dict[key]
        else:
            # Parse datetime fields to ensure they are in the right format
            old_values: list[dict] = db_entity_data_dict.get(key, [])
            new_values: list[dict] = new_entity_data_dict.get(key, [])

            if not new_values:
                continue
            if not old_values:
                db_entity_data_dict[key] = new_values
                continue
            
            # Remove the last_seen field to avoid duplicates
            old_values_without_last_seen = deepcopy(old_values)
            for x in old_values_without_last_seen:
                x.pop("last_seen", None)

            new_values_without_last_seen = deepcopy(new_values)
            for x in new_values_without_last_seen:
                x.pop("last_seen", None)

            # Merge both but only keep unique elements
            for i, value in enumerate(new_values_without_last_seen):
                # If the value is already in the old values, update the last_seen field
                if value in old_values_without_last_seen:
                    # We find the index of the value in the old values. We use this index to update the last_seen field
                    # ! Double read this line if you don't understand it before doing any change !
                    old_values[old_values_without_last_seen.index(value)]["last_seen"] = new_values[i]["last_seen"]
                else:
                    old_values.append(new_values[i])
            db_entity_data_dict[key] = old_values

    if isinstance(new_entity_data, Company):
        # Handle establishments separately if they exist because they are nested
        if new_entity_data.establishments:
            establishments_mapper = {x.establishment_number: x for x in new_entity_data.establishments}
            db_entity_data_dict["establishments"] = [
                _update_entity_object(
                    new_establishment, 
                    establishments_mapper.get(new_establishment.establishment_number)
                )
                for new_establishment in new_entity_data.establishments
            ]
        return Company(**db_entity_data_dict)
    
    elif isinstance(new_entity_data, Establishment):
        return Establishment(**db_entity_data_dict)
    
    else:
        raise TypeError(f"Can't update entity. Type {type(new_entity_data)} is not supported.")


if __name__ == "__main__":
    db_manager = DbManagerMongo()
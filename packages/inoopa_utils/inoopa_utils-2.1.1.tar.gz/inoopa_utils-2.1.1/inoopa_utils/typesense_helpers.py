from typing import Literal
from dotenv import load_dotenv
load_dotenv()

import os
import json
import math
import requests
import typesense
from typesense import exceptions
from typesense.collection import Collection

from inoopa_utils.mongodb_helpers import DbManagerMongo
from inoopa_utils.inoopa_logging import create_logger


class TypesenseManager:
    """
    This class is a client to interact with the Typesense search engine server (deployed in InfraV2).
    
    :attribute typesense_collections: The typesense collection object to interact with the typesense company's collection.
    :attribute mongo_db_collection_name: Mongo DB collection's name to be used. 
    
    :method index_typesense_collection_from_mongo: index mongo_db collection into typesense server.
    :method search_in_typesense_collection: Perform a full text search on the typesense collection.
    """
    def __init__(
        self, 
        host: str = os.environ["TYPESENSE_HOST"],
        port: str = os.environ["TYPESENSE_PORT"], 
        api_key: str = os.environ["TYPESENSE_API_KEY"],
        mongo_db_collection_name: str = "companies_prod",
    ):
        """
        :param host: Typesense's server host
        :param port: Typesense's server port
        :param api_key: Typesense's API key
        :param mongo_db_collection_name : define which MongoDB collection will be used
        """
        self._logger = create_logger("INOOPA.TYPESENSE.CLIENT")
        self._typesense_url = f"{host}:{port}"
        client = typesense.Client({
            'api_key': api_key,
            'nodes': [{
                'host': host,
                'port': port,
                'protocol': 'http'
            }],
            'connection_timeout_seconds': 2
        })
        
        self.typesense_company_collection  = self._create_typesense_collection(mongo_db_collection_name, client)
        self.index_typesense_collection_from_mongo(self.typesense_company_collection)

    def index_typesense_collection_from_mongo(self, typesense_company_collection: Collection) -> None:
        """Will index Typesense collection from mongo's data."""
        mongo_db_manager = DbManagerMongo()
        if typesense_company_collection is None:
            raise TypeError("self.typesense_company_collection is NONE")
        companies_in_mongo = list(mongo_db_manager.company_collection.find())
        self._logger.info(f"{len(companies_in_mongo)} companies found in mongo!")
        self._logger.info("Preprocessing companies...")
        for i, company in enumerate(companies_in_mongo):
            companies_in_mongo[i] = json.loads(json.dumps(companies_in_mongo[i], default=str, ensure_ascii=False))
        
        self._logger.info(f"Indexing: {len(companies_in_mongo)} Companies from mongo...")

        # Divide companies in chunks of 1000
        chunk_size = 1000
        self._logger.info(f"Divide companies in chunks of {chunk_size}...")
        companies_chunks = [companies_in_mongo[i:i+chunk_size] for i in range(0, len(companies_in_mongo), chunk_size)]
        
        for i, companies_chunk in enumerate(companies_chunks):
            self._logger.info(f"Indexing chunk {i+1}/{len(companies_chunks)}...")

            resp = typesense_company_collection.documents.import_(companies_chunk)
            self._logger.debug(f"Indexing {i} response: {resp}")

        self._logger.info("Indexing done!")

    def search_in_typesense_collection(self,
        query: str, 
        query_by: str = "name,name_fr,name_nl,establishments.name,establishments.name_nl,establishments.name_fr",
        element_per_page: int = 20,
        return_type: Literal["json", "ids", "search_results"] = "search_results"
    ) -> list[dict] | list[str] | dict:
        """
        Full text search in typesense collection.

        :param query: the string used to perform the full text search.
        :param query_by: strings used to look for in the query.
        :param element_per_page: int that defines how many elements will be displayed.
        :param return_type : or returns a Json file as list of dicts, or a list of ids, or a dict of results.   
        """
        if self.typesense_company_collection is None:
            raise ValueError("self.typesense_company_collection is NONE")
        results = self.typesense_company_collection.documents.search({
            "q" : query,
            "query_by" : query_by,
            "per_page" : element_per_page,
            "page": 1,
        })

        # Get all results if there are more than x results
        if results["found"] > element_per_page:
            all_results = []
            # from page 2 to last page
            for page in range(2, _get_max_pages(results["found"], element_per_page) + 1):
                result = self.typesense_company_collection.documents.search({
                    "q" : query,
                    "query_by" : query_by,
                    "per_page" : element_per_page,
                    "page": page,
                    })
                all_results.extend(result["hits"])
            results = results.get("hits", []).extend(all_results)

        if return_type == "json":
            return results.get("hits", [])
        elif return_type == "ids":
            return [hit["document"]["_id"] for hit in results.get("hits", [])]
        elif return_type == "search_results":
            return results
        else:
            raise TypeError(f"return_type {return_type} is not supported! Please use 'json', 'ids' or 'search_results'")

    def _check_typesense_server_heatlh(self) -> None:
        """Check if typesense server is up and running."""
        response = requests.get(f"{self._typesense_url }/health")
        response.raise_for_status()
        if response.json()['ok'] != True: 
            raise Exception("Typesense is not running!")

    def _create_typesense_collection(self, collection_name:str, client:typesense.Client) -> Collection :
        """Create a Typesense schema so MongoDB's collection can be interpreted."""
        try :
            client.collections.create({
                "name": collection_name,  
                "fields": [
                    {"optional" : True, "name": "name", "type": "string"},
                    {"optional" : True, "name": "name_fr", "type": "string" },
                    {"optional" : True, "name": "name_nl", "type": "string"},
                    {"optional" : True, "name": "establishments.name", "type": "string[]"},
                    {"optional" : True, "name": "establishments.name_fr", "type": "string[]"},
                    {"optional" : True, "name": "establishments.name_nl", "type": "string[]"},
                    ],
                "enable_nested_fields": True
            })
            self._logger.info(f"Typesense collection {collection_name} created!")
        except exceptions.ObjectAlreadyExists:
            self.companies_typesense_collection = client.collections[collection_name]
            self._logger.info(f"Typesense collection {collection_name} already exists!")
        collection:Collection = client.collections[collection_name] #type:ignore
        return collection


def _get_max_pages(results: int, per_page: int):
    """
    Calculate the maximum number of pages needed to display all results in a paginated search.

    :param results: The total number of results from the search operation in the Typesense collection.
    :param per_page: The number of results to display per page in the search results.

    :return: The maximum number of pages required to display all results, considering the specified number of results per page.
    """
    return math.ceil(results / per_page)


if __name__ == "__main__":
    typesense_manager = TypesenseManager(mongo_db_collection_name="companies_prod")
    search_results = typesense_manager.search_in_typesense_collection("delhaize", return_type="json")
    
    print(len(search_results))
    
    # print(f"Found: {search_results.get('found', 0)}")
    # print(f"hits: {len(search_results.get('hits', []))}")

    # Debug
    with open("./search_results.json", "w") as f:
        json.dump(search_results, f, ensure_ascii=False, indent=4)
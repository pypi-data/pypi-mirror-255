import logging
import requests
import json
from redis import Redis
from requests.structures import CaseInsensitiveDict
from pydash import py_
from ._utils import _is_my_keplive

logger = logging.getLogger(__name__)

import requests

class EmddClient:
    def __init__(
        self,
        api_url="https://api.digigov.grnet.gr",
        api_key=None,
        cache: Redis = None,
        cache_ttl: int = 3600,
        cache_key_prefix="EMDD-MITOS",
    ):
        self._api_url = api_url
        self._api_key = api_key
        self._cache = cache
        self._cache_ttl = cache_ttl
        self._cache_key_prefix = cache_key_prefix

        self._default_headers = CaseInsensitiveDict()
        self._default_headers["Content-Type"] = "application/json"
        self._default_headers["User-Agent"] = "whatever"
        self._default_headers["Cache-Control"] = "no-cache"
        if self._api_key is not None:
            self._default_headers["x-api-key"] = "{}".format(self._api_key)

        self._api_processes_search_url = "{}/v1/services/search".format(self._api_url)
        self._api_processes_url = "{}/v1/services".format(self._api_url)
        self._api_extended_processes_url = "{}/v1/services-extended".format(
            self._api_url
        )
        self._api_organization_url = "{}/v1/organization".format(self._api_url)
        self._api_nace_code_url = "{}/v1/registries/nace".format(self._api_url)
        self._api_sdg_code_url = "{}/v1/registries/sdg".format(self._api_url)
        self._api_unit_url = "{}/v1/unit".format(self._api_url)
        self._api_registries_url = "{}/v1/registry/id".format(self._api_url)
        self._api_evidence_type_url = "{}/v1/registries/evidence".format(self._api_url)
        self._api_provision_org_group_url = (
            "{}/v1/registries/evidence/taxonomy/provision_org_gro".format(self._api_url)
        )

    def _cached(func):
        def wrapper(instance, *args, **kwargs):
            # Generate a unique key for the function based on its arguments
            key = f"{instance._cache_key_prefix}:{func.__name__}:{args}:{kwargs}"

            # Check if the result is already in the cache
            value = None
            if instance._cache is not None:
                result = instance._cache.get(key)
                if result is None:
                    # Run the function and cache the result for next time.
                    value = func(instance, *args, **kwargs)
                    if value is not None:
                        value_json = json.dumps(value, ensure_ascii=False)
                        instance._cache.set(key, value_json, ex=instance._cache_ttl)
                else:
                    # Skip the function entirely and use the cached value instead.
                    value = json.loads(result)
            else:
                # no caching
                value = func(instance, *args, **kwargs)
            return value

        return wrapper

    def _handle_json_response(self, r, default_value=None):
        if r.ok:
            response = r.json()
            if response["success"] is True:
                return response["data"]
            return default_value
        else:
            logger.warning("Failed to acquire: {}".format(r.text))
            return default_value

    @_cached
    def get_unit(self, id):
        logger.debug("Fetching unit {}".format(id))

        return self._handle_json_response(
            requests.get(
                self._api_unit_url,
                params={"id": id},
                headers=self._default_headers,
            )
        )

    @_cached
    def get_sdg_code(self, id):
        logger.debug("Fetching sdg code {}".format(id))

        return self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_sdg_code_url, id),
                headers=self._default_headers,
            )
        )

    @_cached
    def get_nace_code(self, id):
        logger.debug("Fetching nace code {}".format(id))

        return self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_nace_code_url, id),
                headers=self._default_headers,
            )
        )

    @_cached
    def get_organization(self, id):
        logger.debug("Fetching organization {}".format(id))

        return self._handle_json_response(
            requests.get(
                self._api_organization_url,
                params={"id": id},
                headers=self._default_headers,
            )
        )

    @_cached
    def get_registry(self, id):
        logger.debug("Fetching registry {}".format(id))

        return self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_registries_url, id),
                headers=self._default_headers,
            )
        )

    @_cached
    def get_evidence_type(self, id):
        logger.debug("Fetching evidence type {}".format(id))

        return self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_evidence_type_url, id),
                headers=self._default_headers,
            )
        )

    @_cached
    def get_provision_org_group(self, id):
        logger.debug("Fetching provision org group {}".format(id))

        response = self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_provision_org_group_url, id),
                headers=self._default_headers,
            )
        )
        if response is not None and "children" in response:
            response.pop("children")
        return response

    @_cached
    def get_process_list(self, limit=None, filter=None):
        logger.debug("Acquiring list of EMD processes")
        url = self._api_processes_url
        if filter is not None:
            url = "{}/filter/{}".format(self._api_processes_search_url, filter)

        params = {}
        if limit is not None:
            params["limit"] = limit

        return self._handle_json_response(
            requests.get(url, headers=self._default_headers, params=params), []
        )

    @_cached
    def get_process(self, id, english=False, embedded=True, use_fallback=True):
        logger.debug("Acquiring process {}".format(id))

        params = {}
        if english is True:
            params["lang"] = "en"

        response = self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_processes_url, id),
                headers=self._default_headers,
                params=params,
            ),
        )
        if response is not None and embedded is True:
            response = self._transform_process(response, use_fallback=use_fallback)

        return response

    @_cached
    def get_extended_process(self, id, english=False):
        logger.debug("Acquiring extended process {}".format(id))

        params = {}
        if english is True:
            params["lang"] = "en"

        response = self._handle_json_response(
            requests.get(
                "{}/{}".format(self._api_extended_processes_url, id),
                headers=self._default_headers,
                params=params,
            ),
        )
        if response is not None:
            response = self._transform_extended_process(response)

        return response

    def _transform_process(self, payload, use_fallback=True):
        # map org_owner
        py_.set(
            payload,
            "metadata.process.org_owner",
            self._map_to_embedded(
                py_.get(payload, "metadata.process.org_owner"),
                self.get_organization,
                use_fallback=use_fallback,
            ),
        )

        # map provision_org
        py_.set(
            payload,
            "metadata.process.provision_org",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_organization, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.provision_org", []),
                )
            ),
        )

        # map provision_org_group
        py_.set(
            payload,
            "metadata.process.provision_org_group",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_provision_org_group, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.provision_org_group", []),
                )
            ),
        )

        # map provision_org_group_remote
        py_.set(
            payload,
            "metadata.process.provision_org_group_remote",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_provision_org_group, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.provision_org_group_remote", []),
                )
            ),
        )

        if _is_my_keplive(payload):
            py_.set(payload, 'metadata.process.is_served_via_mykeplive', True)

        # map provision_org_group_remote
        py_.set(
            payload,
            "metadata.process.provision_org_owner_directory",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_unit, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.provision_org_owner_directory", []),
                )
            ),
        )

        # map nace_codes
        py_.set(
            payload,
            "metadata.process.nace_codes",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_nace_code, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.nace_codes", []),
                )
            ),
        )

        # map sdg_codes
        py_.set(
            payload,
            "metadata.process.sdg_codes",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_sdg_code, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.sdg_codes", []),
                )
            ),
        )

        # map output_registries
        py_.set(
            payload,
            "metadata.process.output_registries",
            list(
                map(
                    lambda id: self._map_to_embedded(
                        id, self.get_registry, use_fallback=use_fallback
                    ),
                    py_.get(payload, "metadata.process.output_registries", []),
                )
            ),
        )

        def map_evidence(ev):
            logger.debug("Mapping evidence={}".format(ev))
            ev_type = ev.get("evidence_type")
            if ev_type is not None:
                ev["evidence_type"] = self._map_to_embedded(
                    ev_type, self.get_evidence_type, use_fallback=use_fallback
                )
            return ev
        
        # map evidence types
        py_.set(
            payload,
            "metadata.process_evidences",
            list(
                map(
                    map_evidence,
                    py_.get(payload, "metadata.process_evidences", []),
                )
            ),
        )

        return payload

    def _transform_extended_process(self, payload):
        
        if _is_my_keplive(payload):
            py_.set(payload, 'metadata.process.is_served_via_mykeplive', True)

  
    def _map_to_embedded(
        self,
        id,
        func,
        use_fallback=True,
    ):
        try:
            return func(id)
        except:
            pass
        if use_fallback is True:
            return {
                "id": id,
                "title": {
                    "el": str(id),
                    "en": str(id),
                },
            }
        return id

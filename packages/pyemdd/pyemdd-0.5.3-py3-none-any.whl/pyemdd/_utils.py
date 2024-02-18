import logging
from pydash import py_

logger = logging.getLogger(__name__)

def _is_my_keplive(payload):
    provision_org_group = py_.get(
        payload,
        'metadata.process.provision_org_group',
        [],
    )
    provision_org_group_remote = py_.get(
        payload,
        'metadata.process.provision_org_group_remote',
        [],
    )
    is_my_keplive = False;
    if len(provision_org_group) > 0:
        for org_group in provision_org_group:
            if org_group["id"] == "8256":
                is_my_keplive = True
                break

            if py_.get(org_group, "title.el", "") == 'myKEPlive':
                is_my_keplive = True
                break

    if (is_my_keplive is False and len(provision_org_group_remote) > 0):
        for org_group in provision_org_group_remote:
            if org_group["id"] == '8256':
                is_my_keplive = True
                break
            
            if py_.get(org_group, "title.el", "") == 'myKEPlive':
                is_my_keplive = True
                break

    return is_my_keplive


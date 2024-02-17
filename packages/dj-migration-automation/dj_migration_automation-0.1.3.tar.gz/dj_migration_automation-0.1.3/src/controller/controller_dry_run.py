"""
As discussed before, and also discussed with Kewal yesterday.
1) Implementation team needs an API for running canister recommendation for existing canister arrangement.
As discussed, this API shouldn't change anything in DB,
it will be like a dry run.
The API will use all the canisters, it won't look for system constraint in this.
2) They also need API by which they can know how many canisters the
system requires for achieving 50-50 split, which is same as canister registration API.
The only difference is we will provide the only count instead of a list of canisters to register.
3) Apart from that, they also want to know that for current configuration
if they don't transfer any canister what will be split.
I guess this will be the scenario when we skip all the transfers.

"""
import cherrypy

from dosepack.error_handling.error_handler import create_response
from src.service.dry_run import pack_distribution, register_canisters, register_canisters_optimised


class DryRun(object):
    """
    All Dry runs
    """

    @cherrypy.expose('packdistribution')
    def pack_distribution(self, company_id, batch_ids):
        response = pack_distribution(company_id, batch_ids=batch_ids)
        return create_response(response)

    @cherrypy.expose('registercanister')
    def register_canister_recommendation(self, company_id, batch_id):
        response = register_canisters(company_id, batch_id)
        return response

    @cherrypy.expose('registercanisteroptimised')
    def register_canister_recommendation(self, company_id, batch_id, number_of_drugs_needed=None,
                                         drugs_to_register=None):
        response = register_canisters_optimised(company_id, batch_id, number_of_drugs_needed, drugs_to_register)
        return response

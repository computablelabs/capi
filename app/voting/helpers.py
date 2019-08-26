from flask import g, current_app
from computable.contracts import Voting

def filter_candidate_added(from_block, arg_filters=None):
    """
    given filter args and the current request g context create a voting contract
    and execute the filter for candidate added event, returning the results
    """

    voting = Voting(g.w3.eth.defaultAccount)
    voting.at(g.w3, current_app.config['VOTING_CONTRACT_ADDRESS'])
    if arg_filters != None:
        filter = voting.deployed.events.CandidateAdded.createFilter(fromBlock=from_block, argument_filters=arg_filters)
    else:
        filter = voting.deployed.events.CandidateAdded.createFilter(fromBlock=from_block)

    return filter.get_all_entries()

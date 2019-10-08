"""
Abstractions and operations, which may or may not be protocol related, specific to the voting namespace
"""
from flask import g, current_app
from computable.contracts import Voting
from core.protocol import get_voting

def filter_candidate_added(from_block, arg_filters=None):
    """
    given filter create a voting contract
    and execute the filter for candidate added event, returning the results
    """
    v = get_voting()
    if arg_filters != None:
        filter = v.deployed.events.CandidateAdded.createFilter(fromBlock=from_block, argument_filters=arg_filters)
    else:
        filter = v.deployed.events.CandidateAdded.createFilter(fromBlock=from_block)

    return filter.get_all_entries()

def filter_candidate_removed(from_block):
    """
    given filter create a voting contract
    and execute the filter for candidate removed event, returning the results
    """
    v = get_voting()
    filter = v.deployed.events.CandidateRemoved.createFilter(fromBlock=from_block)

    return filter.get_all_entries()



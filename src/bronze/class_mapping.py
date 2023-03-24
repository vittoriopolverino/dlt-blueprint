"""
Module containing a collection of classes used throughout the project.
Include here all classes that may be dynamically loaded based on their name as a string.
"""

from src.bronze.contact import Contact
from src.bronze.email import Email
from src.bronze.hype_casestatus import HypeCasestatus
from src.bronze.hype_category import HypeCategory
from src.bronze.hype_corebankingstatus import HypeCorebankingStatus
from src.bronze.hype_emoneyaccount import HypeEmoneyaccount
from src.bronze.hype_pack import HypePack
from src.bronze.hype_product import HypeProduct
from src.bronze.hype_statustransitionlog import HypeStatustransitionlog
from src.bronze.hype_subcategory import HypeSubcategory
from src.bronze.hype_tag import HypeTag
from src.bronze.incident import Incident
from src.bronze.queue import Queue
from src.bronze.systemuser import Systemuser
from src.bronze.team import Team

# Mapping of class names to class objects for the Bronze layer
class_name = {
    'contact': Contact,
    'email': Email,
    'hype_casestatus': HypeCasestatus,
    'hype_category': HypeCategory,
    'hype_corebankingstatus': HypeCorebankingStatus,
    'hype_emoneyaccount': HypeEmoneyaccount,
    'hype_pack': HypePack,
    'hype_product': HypeProduct,
    'hype_statustransitionlog': HypeStatustransitionlog,
    'hype_subcategory': HypeSubcategory,
    'hype_tag': HypeTag,
    'incident': Incident,
    'queue': Queue,
    'systemuser': Systemuser,
    'team': Team,
}

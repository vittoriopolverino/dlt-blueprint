"""
Module containing a collection of classes used throughout the project.
Include here all classes that may be dynamically loaded based on their name as a string.
"""

from src.silver.contact import Contact
from src.silver.email import Email
from src.silver.hype_casestatus import HypeCasestatus
from src.silver.hype_category import HypeCategory
from src.silver.hype_corebankingstatus import HypeCorebankingStatus
from src.silver.hype_emoneyaccount import HypeEmoneyaccount
from src.silver.hype_pack import HypePack
from src.silver.hype_product import HypeProduct
from src.silver.hype_statustransitionlog import HypeStatustransitionlog
from src.silver.hype_subcategory import HypeSubcategory
from src.silver.hype_tag import HypeTag
from src.silver.incident import Incident
from src.silver.queue import Queue
from src.silver.systemuser import Systemuser
from src.silver.team import Team

# Mapping of class names to class objects for the Silver layer
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

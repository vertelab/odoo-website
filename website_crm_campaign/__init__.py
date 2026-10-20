# Absolut import -> relativ (2026-10-20). campaign.py ligger i modulens
# rotkatalog, så Python 3 hittar den inte med `import campaign`:
#   ModuleNotFoundError: No module named 'campaign'
from . import campaign

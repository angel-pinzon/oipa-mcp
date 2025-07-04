"""
Connectors package for OIPA integration

Provides various connection methods to OIPA:
- database.py: Direct Oracle database connection
- web_service.py: FileReceived SOAP web service  
- push_framework.py: Push Framework integration
"""

from .database import OipaDatabase, OipaQueryBuilder, oipa_db

__all__ = [
    "OipaDatabase", 
    "OipaQueryBuilder",
    "oipa_db"
]

"""
Trippa Booking Bot - Main Package
Automated booking system for Trattoria Trippa Milano
"""

__version__ = "1.1.2"
__author__ = "Domenico Angri"

from .api import ResDiaryClient, ENDPOINTS

__all__ = ['api', 'bot', 'utils', 'notifiers']
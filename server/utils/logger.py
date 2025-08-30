#!/usr/bin/env python3
"""
Logger - Logging-Konfiguration für VR Gaming Server
"""
import logging
import sys
from pathlib import Path

def setup_logging():
    """Logging für den gesamten Server einrichten"""
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/server.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Spezielle Logger für verschiedene Komponenten
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging-System initialisiert")

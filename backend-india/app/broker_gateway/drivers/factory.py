"""
QuantView Broker Gateway — Broker Factory Pattern

Instantiates and returns the concrete broker driver based on the requested broker code.
"""

from typing import Dict, Type
from app.broker_gateway.drivers.base import BaseBrokerDriver
from app.broker_gateway.schemas.normalized import BrokerCode


class BrokerFactory:
    """Factory Pattern registry to instantiate broker drivers dynamically."""

    _drivers: Dict[BrokerCode, Type[BaseBrokerDriver]] = {}

    @classmethod
    def register(cls, broker_code: BrokerCode):
        """Decorator to register broker drivers."""
        def decorator(driver_cls: Type[BaseBrokerDriver]):
            cls._drivers[broker_code] = driver_cls
            return driver_cls
        return decorator

    @classmethod
    def get_driver(
        cls,
        broker_code: BrokerCode,
        connection_id: str,
        account_id: str,
        access_token: str,
        api_key: str,
        **kwargs
    ) -> BaseBrokerDriver:
        """Instantiates concrete driver for given broker code."""
        code_enum = BrokerCode(broker_code) if isinstance(broker_code, str) else broker_code
        if code_enum not in cls._drivers:
            raise ValueError(f"Unsupported broker: '{broker_code}'. Registered: {list(cls._drivers.keys())}")

        driver_cls = cls._drivers[code_enum]
        return driver_cls(
            connection_id=connection_id,
            account_id=account_id,
            access_token=access_token,
            api_key=api_key,
            **kwargs
        )

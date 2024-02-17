"""
    Events
"""
from enum import Enum
from typing import Callable, Any

EventKey = Enum | str

_event_handler_registry:dict[Enum,list[Callable]] = dict()

#--------------------------------------------------------------------------------------------------
def subscribe(eventkey:EventKey, handler:Callable[[EventKey,str,Any],None]):
    if eventkey not in _event_handler_registry.keys():
        _event_handler_registry[eventkey] = []
    
    elif handler in _event_handler_registry[eventkey]:
        raise Exception(f'Event {eventkey} handler is already registered')
    
    _event_handler_registry[eventkey].append(handler)

#--------------------------------------------------------------------------------------------------
def unsubscribe(handler:Callable[[EventKey,str,Any],None], eventkey:EventKey):
    handlers = _event_handler_registry[eventkey]
    if handler in handlers: handlers.remove(handler)
    if len(handlers) == 0: _event_handler_registry[eventkey].remove()

#--------------------------------------------------------------------------------------------------
def publish(eventkey:EventKey, source:str, data:Any):
    handlers = _event_handler_registry.get(eventkey)
    if handlers is not None and len(handlers) > 0:
        for handler in handlers: handler(eventkey, source, data)
    
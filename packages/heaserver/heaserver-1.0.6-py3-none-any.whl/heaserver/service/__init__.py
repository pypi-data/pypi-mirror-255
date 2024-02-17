"""
HEA Server Framework is a framework library for creating HEA microservices.

Types of microservices

The registry microservice manages a listing of all microservices that the
current instance of HEA knows about.

Trash microservices serve items that have been marked for permanent deletion but
have not been permanently deleted yet. The registry service may have at most
one trash microservice registered for a given desktop object type, file system
type, and file system name combination. Desktop object types with no registered
trash microservice are assumed not to have a trash and are deleted permanently.

Class in this package and all microservices have the following conventions for object attributes:
* Private attributes' names are prefixed with a double underscore.
* Protected attributes' names are prefixed with a single underscore. "Protected" is defined as accessible only to
the class in which it's defined and subclasses. Python does not enforce protected access, but uses of protected
attributes outside of subclasses may break even in patch releases.
"""
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

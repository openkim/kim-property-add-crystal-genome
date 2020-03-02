"""Create module."""

import os
from os.path import join, isfile

from .definition import KIMPropertyError, check_property_definition
from .instance import get_property_id_path, check_instance_id_format

from .pickle import unpickle_kim_properties

try:
    import kim_edn
except:
    msg = '\nERROR: Failed to import the `kim_edn` utility module.'
    raise KIMPropertyError(msg)

__all__ = [
    "get_properties",
    "kim_property_create",
    "unset_property_id",
]

kim_properties = None
"""dict: KIM properties dictionary indexed by properties full IDs."""

property_name_to_property_id = None
"""dict: KIM properties name to full ID dictionary."""

property_id_to_property_name = None
"""dict: KIM properties full ID to name dictionary."""

# Get the standard KIM properties
kim_properties, property_name_to_property_id, property_id_to_property_name = unpickle_kim_properties()

new_property_ids = None
"""list: Newly added property IDs """


def get_properties():
    """Get the reconstituted kim properties object hierarchy from the pickled object.

    Returns:
        dict -- kim_properties.
    """
    global kim_properties
    return kim_properties


def unset_property_id(property_id):
    """Unset a property with a "property_id" from kim properties.

    If a requested property with a "property_id" is a newly created
    property, then it will remove that property from kim_properties,
    otherwise it does nothing.

    Arguments:
        property_id {string} -- KIM property-id, a string containing the
            unique ID of the property.

    """
    global new_property_ids
    if new_property_ids is not None:
        if property_id in new_property_ids:
            del kim_properties[property_id]
            _name = property_id_to_property_name[property_id]
            del property_name_to_property_id[_name]
            del property_id_to_property_name[property_id]
            new_property_ids.remove(property_id)
            if len(new_property_ids) == 0:
                new_property_ids = None


def kim_property_create(instance_id, property_name, property_instances=None):
    """Create a new kim property instance.

    It takes as input the property instance ID and property definition name
    and creates initial property instance data structure. If the
    "property_instances" obj is already exist it adds the newly created
    property instance to the obj and fails if it already exist there.

    For example::

    >>> kim_property_create(1, 'cohesive-energy-relation-cubic-crystal')
    '[{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal" "instance-id" 1}]'

    >>> str = kim_property_create(1, 'cohesive-energy-relation-cubic-crystal')

    Creating and addition of a second property instance::

    >>> kim_property_create(2, 'atomic-mass', str)
    '[{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal" "instance-id" 1} {"property-id" "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass" "instance-id" 2}]'

    >>> str = kim_property_create(2, 'atomic-mass', str)
    >>> obj = kim_edn.loads(str)
    >>> print(kim_edn.dumps(obj, indent=4))
    [
        {
            "property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal"
            "instance-id" 1
        }
        {
            "property-id" "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass"
            "instance-id" 2
        }
    ]

    Arguments:
        instance_id {int} -- A positive integer identifying the property
            instance.
        property_name {string} --
            - A string containing the property name or
            - unique ID of the property, or
            - a path-like object giving the pathname (absolute or relative to
              the current working directory) of the file to be opened
        property_instances {string} -- A string containing the serialized
            KIM-EDN formatted property instances. (default: {None})

    Returns:
        string -- serialized KIM-EDN formatted property instances.

    """
    global kim_properties
    global property_name_to_property_id
    global property_id_to_property_name
    global new_property_ids

    if not isinstance(instance_id, int):
        msg = '\nERROR: the "instance_id" is not an `int`.'
        raise KIMPropertyError(msg)

    # Check instance id format to prevent mistakes as early as possible
    check_instance_id_format(instance_id)

    if not isinstance(property_name, str):
        msg = '\nERROR: the "property_name" is not an `str`.'
        raise KIMPropertyError(msg)

    if property_instances is None:
        kim_property_instances = []
    else:
        # Deserialize the KIM property instances.
        kim_property_instances = kim_edn.loads(property_instances)

        for a_property_instance in kim_property_instances:
            if instance_id == a_property_instance["instance-id"]:
                msg = '\nERROR: the "instance-id"’s cannot repeat. '
                msg += 'In the case where there are multiple property '
                msg += 'instances, the instance-id’s cannot repeat.'
                raise KIMPropertyError(msg)

    # KIM property names.
    kim_property_names = [k for k in property_name_to_property_id]

    # KIM property full IDs.
    kim_property_ids = [k for k in property_id_to_property_name]

    new_property_instance = {}

    # If the property_name is a path-like object to a file to be opened
    if isfile(property_name):
        # Load the property definition from a file
        pd = kim_edn.load(property_name)

        # Check the correctness of th eproperty definition
        check_property_definition(pd)

        # Get the property ID
        _property_id = pd["property-id"]

        # Check to make sure that this property does not exist in OpenKIM
        if _property_id in kim_properties:
            msg = '\nERROR: the input property_name file contains a '
            msg += 'property ID which already exists in OpenKIM.'
            msg += 'Use the KIM Property Definition or update the ID in the'
            msg += 'property_name file.\n'
            msg += 'See the KIM Property Definitions at '
            msg += 'https://openkim.org/properties for more detailed '
            msg += 'information.'
            raise KIMPropertyError(msg)

        # Add the new property definition to kim_properties
        kim_properties[_property_id] = pd

        # Get the property name
        _, _, _, _property_name = get_property_id_path(_property_id)

        property_name_to_property_id[_property_name] = _property_id
        property_id_to_property_name[_property_id] = _property_name

        kim_property_names.append(_property_name)
        kim_property_ids.append(_property_id)

        # Keep the record of a newly added properties
        if new_property_ids is None:
            new_property_ids = []
        new_property_ids.append(_property_id)

        # Set the new instance property ID
        new_property_instance["property-id"] = _property_id
    else:
        if property_name in kim_property_names:
            new_property_instance["property-id"] = property_name_to_property_id[property_name]
        elif property_name in kim_property_ids:
            new_property_instance["property-id"] = property_name
        else:
            msg = '\nERROR: the requested "property_name" :\n'
            msg += '"{}"\n'.format(property_name)
            msg += 'is not a valid KIM property name nor '
            msg += 'a path-like object to a file.\n '
            msg += 'See the KIM Property Definitions at '
            msg += 'https://openkim.org/properties for more detailed '
            msg += 'information.'
            raise KIMPropertyError(msg)

    new_property_instance["instance-id"] = instance_id

    # Add the newly created property instance to the collection
    kim_property_instances.append(new_property_instance)

    # If there are multiple keys sort them based on instance-id
    if (len(kim_property_instances) > 1):
        kim_property_instances = sorted(
            kim_property_instances, key=lambda i: i["instance-id"])

    # Return the serialize KIM property instances
    return kim_edn.dumps(kim_property_instances)

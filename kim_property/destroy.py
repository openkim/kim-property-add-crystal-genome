"""Destroy module."""

from .definition import KIMPropertyError
from .create import unset_property_id

try:
    import kim_edn
except:
    msg = '\nERROR: Failed to import the `kim_edn` utility module.'
    raise KIMPropertyError(msg)

__all__ = [
    "kim_property_destroy",
]


def kim_property_destroy(property_instances, instance_id):
    """Destroy a kim property instance.

    Delete a previously created property instance.

    For example::

    >>> obj = '[{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal" "instance-id" 1}]'

    >>> kim_property_destroy(obj, 1)
    '[]'

    >>> obj = '[{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal" "instance-id" 1} {"property-id" "tag:brunnels@noreply.openkim.org,2016-05-11:property/atomic-mass" "instance-id" 2}]'

    >>> kim_property_destroy(obj, 2)
    '[{"property-id" "tag:staff@noreply.openkim.org,2014-04-15:property/cohesive-energy-relation-cubic-crystal" "instance-id" 1}]'

    Arguments:
        property_instances {string} -- A string containing the serialized
        KIM-EDN formatted property instances.
        instance_id {int} -- A positive integer identifying the property
        instance.

    Returns:
        string -- serialized KIM-EDN formatted property instances.

    """
    if not isinstance(instance_id, int):
        msg = '\nERROR: the "instance_id" is not an `int`.'
        raise KIMPropertyError(msg)

    if property_instances is None or \
            property_instances == 'None' or \
            property_instances == '' or \
            property_instances == '[]':
        return '[]'

    # Deserialize the KIM property instances.
    kim_property_instances = kim_edn.loads(property_instances)

    for a_property_instance in kim_property_instances:
        if instance_id == a_property_instance["instance-id"]:
            property_id = a_property_instance["property-id"]
            unset_property_id(property_id)
            kim_property_instances.remove(a_property_instance)

    # Return the serialize KIM property instances
    return kim_edn.dumps(kim_property_instances)

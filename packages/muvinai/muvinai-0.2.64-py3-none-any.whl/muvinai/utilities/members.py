from typing import Optional

from deepdiff import DeepDiff
from deepdiff.helper import notpresent
from deepdiff.model import DiffLevel

from ..service import Cliente
from .dates import today_argentina
from .format import datetime_parser, json_serial
from .init_creds import init_mongo

db = init_mongo()


def member_unsubscribe(member: dict, reason, source, unsubscribe_request=False, status_boleta_inactivado='expired'):
    """ Da de baja un socio modificando los parámetros necesarios
       :param member: objeto de cliente a dar de baja
       :type receiver: dict
       :param reason: motivo de la baja
       :type template: str
       :param unsubscribe_request: es True si el cliente es 'baja' y puede seguir ingresando
       :type unsubscribe_request: bool, optional
       :return: None
       :rtype: None
       """

    status = 'baja' if unsubscribe_request else 'inactivo'

    history_event = create_history_event(member, status, source, reason)

    db.clientes.update_one(
        {"_id": member["_id"]},
        {
            "$push": {
                "history": history_event
            },
            "$set": {
                "next_payment_date": None,
                "status": status
            }
        }
    )

    db.boletas.update_many(
        {
            "member_id": member["_id"],
            "status": {
                "$in": ["error", "rejected", "pending_efectivo", "restored"]
            }
        },
        {
            "$set": {
                "status": status_boleta_inactivado
            }
        }
    )

    if not unsubscribe_request:
        plan_db = db.planes.find_one(member['active_plan_id'])
        if plan_db['nivel_de_acceso'].lower() == 'flex':
            cliente = Cliente(member)
            boleta = cliente.crear_boleta('pending_accesos')
            if boleta.final_price != 0:
                if member['status'] == 'baja':
                    boleta.pagar()
                else:
                    boleta.set_status('expired')
                boleta.push_to_db()


def create_history_event(member, event_type, source, reason=None):
    if event_type == 'inactivo':
        event_type = 'inactivacion'

    history_event = {
        'event': event_type,
        'date_created': today_argentina(),
        'source': source
    }
    if reason:
        history_event["reason"] = reason

    if event_type in ['alta', 'baja', 'inactivacion', 'revertir_baja']:
        history_event['plan'] = member["active_plan_id"]

        if 'discounts' in member and member["discounts"] and len(member["discounts"]) > 0:
            history_event['discounts'] = member['discounts']

    elif event_type == "cambio_tarjeta":
        history_event["card_id"] = member["active_card"]

    return history_event


def version_control(old_doc, new_doc, current_user, source="API") -> Optional[dict]:
    """
    Funcion que implementa el control de versiones para los clientes de la base de datos(MongoDB).

    Parameters:
        old_doc (dict): el documento original en la base de datos.
        new_doc (dict): el documento modificado que se va a almacenar en la base de datos.
        current_user (str): representa al usuario que realizó la modificación.
        source (str): la fuente de la modificación (API, web, base de datos, etc.). Por defecto es "API".

    Returns:
        vc: un objeto de diccionarios que representan los cambios realizados en el documento, si hay muchos cambios se añidan en un lista (changes).
    """

    excluded_keys = ["history", "version_control", "whitelist"]

    def add_change(change_type: str, change: DiffLevel):
        root_key = change.get_root_key()

        return {
            "field": root_key,
            "previous_value": change.t1 if change.t1 != notpresent else None,
            "new_value": change.t2 if change.t2 != notpresent else None,
            "change_type": change_type,
        }

    if not all(isinstance(doc, dict) for doc in [old_doc, new_doc]):
        return None

    old_doc = json_serial(old_doc)
    new_doc = json_serial(new_doc)

    ddiff = DeepDiff(old_doc, new_doc, view='tree', ignore_order=True, exclude_paths=excluded_keys)

    vc = {
        "source": source,
        "modified_at": today_argentina(),
        "modified_by": current_user,
        "changes": []
    }

    for change_type, items in ddiff.items():
        for change in items:
            change_data = add_change(change_type, change)
            if change_data:
                vc['changes'].append(change_data)

    if vc.get("changes"):
        return datetime_parser(vc)

    return None

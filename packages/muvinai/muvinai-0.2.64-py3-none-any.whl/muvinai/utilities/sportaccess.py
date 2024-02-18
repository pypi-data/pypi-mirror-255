from datetime import datetime

import requests

from .dates import arg_tz, today_argentina
from .init_creds import init_mongo

db = init_mongo()


def consulta_socio_proclub(documento: str) -> dict:
    """ Obtener un socio de la base de datos de sportclub
    :param documento: numero de documento del socio que buscado
    :type documento: str
    :return: respuesta de ProClub (puede ser un socio o None)
    :rtype: dict
    """
    url = "https://apisocios.sportclub.com.ar/members?Documento="
    headers = {
        "x-api-key": "VHGFDn_2212FFF**/-FFFF",
        "Content-Type": "application/json"
    }
    r = requests.get(url + documento, headers=headers)

    if r.status_code >= 400:
        print('Error en consulta_socio_proclub. status_code = ', r.status_code, 'Respuesta: ', r)
        return {}

    try:
        r = r.json()
    except requests.exceptions.JSONDecodeError as e:
        print('Se atrapo una excepcion llamando a proclub. ERROR:', str(e))
        return {}

    if not r.get("data"):
        print('Error en consulta_socio_proclub. No hay data. status_code = ', r["code"], 'Respuesta: ', r)
        return {}

    proclub: dict = r["data"][0]
    spice = proclub.get("CredencialSpice")

    sede_socio = db.club.find_one({"sportaccess_id": int(proclub["Sede-SqlId"])})
    if sede_socio:
        sede_id = sede_socio["_id"]
        sede_name = sede_socio["name"]
    else:
        sede_id = "n/a"
        sede_name = "n/a"

    na = proclub["nivel_acceso"].lower()
    fv = datetime.strptime(proclub['Vigencia'], '%d/%m/%Y').replace(tzinfo=arg_tz, hour=15)
    status = "activo" if fv > today_argentina() else "inactivo"

    deuda_promocion = proclub.get("QntDeudaPromocion", 0)
    deuda_arancel = proclub.get("QntDeudaArancel", 0)

    # Intentamos conversión a formato perfilsocio
    socio = {
        "_id": None,
        "status": status,
        "fecha_vigencia": fv,
        "last_subscription_date": datetime.strptime(proclub["FechaIngreso"], '%d/%m/%Y').replace(tzinfo=arg_tz, hour=15),
        "apto_medico": {
            "fecha_vigencia": datetime.strptime(proclub['AptoMedico'], '%d/%m/%Y').replace(tzinfo=arg_tz, hour=15)
        },
        "apellido": proclub["Apellido"],
        "documento": documento,
        "nombre": proclub["Nombre"],
        "email": proclub["Mail"],
        "plan_details": {
            "nivel_de_acceso": na,
            "name": proclub["Plan"],
            "merchant_id": None,
            "sede_local_name": sede_name if na == "local" else None,
            "sede_local": sede_id if na == "local" else None,
            "convenio": proclub["Convenio"],
            "vertical": "Corporativo" if proclub["Convenio"] else "otros"
        },
        "token_spice": spice,
        "seller_merchant": None,
        "externo": True,
        "terceros": proclub["Terceros"],
        "telefono": proclub.get("Telefono"),
        "sede_sqlid": proclub["Sede-SqlId"],
        "sede_socio_name": sede_name,
        "sede_socio": sede_id,
        "proclub_id": proclub["NroSocio"],
        "deuda_promocion": deuda_promocion,
        "deuda_arancel": deuda_arancel
    }

    return socio


def update_spice(nro_socio: str, spice) -> dict:
    """ Obtener un socio de la base de datos de sportclub
    :param documento: numero de documento del socio que buscado
    :type documento: str
    :return: respuesta de SpAccess (puede ser un socio o un mensaje de error)
    :rtype: dict
    """
    url = "https://apisocios.sportclub.com.ar/members?NroSocio="
    headers = {
        "x-api-key": "VHGFDn_2212FFF**/-FFFF",
        "Content-Type": "application/json"
    }
    body = {"Credencial_spice": spice}
    r = requests.put(f"{url}{nro_socio}", headers=headers, json=body)
    return r

import base64
import json
import os

from cryptography.hazmat.primitives import serialization


def _obtener_clave_privada():
    ruta = os.getenv("STOCKLY_PRIVATE_KEY_PATH", "").strip()

    if not ruta:
        raise RuntimeError(
            "No se configuró STOCKLY_PRIVATE_KEY_PATH."
        )

    if not os.path.exists(ruta):
        raise RuntimeError(
            "No se encontró la clave privada de Stockly."
        )

    with open(ruta, "rb") as archivo:
        private_key = serialization.load_pem_private_key(
            archivo.read(),
            password=None,
        )

    return private_key


def crear_payload_licencia(licencia, dispositivo):
    payload = {
        "version": 1,
        "codigo": licencia.codigo,
        "installation_id": dispositivo.installation_id,
        "estado": licencia.estado_efectivo,
        "fecha_activacion": licencia.fecha_activacion.isoformat(),
        "fecha_vencimiento": licencia.fecha_vencimiento.isoformat(),
    }

    payload_bytes = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return payload, payload_bytes


def firmar_licencia(licencia, dispositivo):
    private_key = _obtener_clave_privada()

    payload, payload_bytes = crear_payload_licencia(
        licencia,
        dispositivo,
    )

    signature = private_key.sign(payload_bytes)

    return {
        "payload": payload,
        "payload_base64": base64.b64encode(
            payload_bytes
        ).decode("ascii"),
        "signature_base64": base64.b64encode(
            signature
        ).decode("ascii"),
        "algoritmo": "Ed25519",
    }

def verificar_firma(
    payload_base64,
    signature_base64,
    public_key_path,
):
    payload_bytes = base64.b64decode(
        payload_base64
    )

    signature = base64.b64decode(
        signature_base64
    )

    with open(public_key_path, "rb") as archivo:
        public_key = serialization.load_pem_public_key(
            archivo.read()
        )

    try:
        public_key.verify(
            signature,
            payload_bytes,
        )

        return True

    except Exception:
        return False
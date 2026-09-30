import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import (
    ErrorActivacion,
    ErrorValidacion,
    activar_licencia,
    validar_licencia,
)
from .crypto import firmar_licencia


@csrf_exempt
@require_POST
def activar(request):
    try:
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "ok": False,
                    "mensaje": "El cuerpo de la solicitud no contiene JSON válido.",
                },
                status=400,
            )

        codigo = str(
            data.get("codigo", "")
        ).strip()

        installation_id = str(
            data.get("installation_id", "")
        ).strip()

        version_app = str(
            data.get("version_app", "")
        ).strip()

        nombre_dispositivo = str(
            data.get("nombre_dispositivo", "")
        ).strip()
        plataforma = str(
            data.get("plataforma", "")
        ).strip()

        licencia, dispositivo = activar_licencia(
            codigo=codigo,
            installation_id=installation_id,
            version_app=version_app,
            nombre_dispositivo=nombre_dispositivo,
            plataforma=plataforma,
            request=request,
        )

        licencia_firmada = firmar_licencia(
            licencia,
            dispositivo,
        )

        return JsonResponse(
            {
                "ok": True,
                "mensaje": "Licencia activada correctamente.",
                "licencia": {
                    "codigo": licencia.codigo,
                    "estado": licencia.estado_efectivo,
                    "cliente": str(licencia.cliente),
                    "meses_vigencia": licencia.meses_vigencia,
                    "fecha_activacion": (
                        licencia.fecha_activacion.isoformat()
                        if licencia.fecha_activacion
                        else None
                    ),
                    "fecha_vencimiento": (
                        licencia.fecha_vencimiento.isoformat()
                        if licencia.fecha_vencimiento
                        else None
                    ),
                },
                "dispositivo": {
                    "installation_id": dispositivo.installation_id,
                    "nombre": dispositivo.nombre_dispositivo,
                    "plataforma": dispositivo.plataforma,
                    "version_app": dispositivo.version_app,
                },
                "licencia_firmada": licencia_firmada,
            },
            status=200,
        )

    except ErrorActivacion as error:
        return JsonResponse(
            {
                "ok": False,
                "mensaje": str(error),
            },
            status=400,
        )

    except Exception:
        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Ocurrió un error interno al procesar la activación.",
            },
            status=500,
        )

@csrf_exempt
@require_POST
def validar(request):
    try:
        try:
            data = json.loads(request.body or "{}")

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "ok": False,
                    "mensaje": "El cuerpo de la solicitud no contiene JSON válido.",
                },
                status=400,
            )

        codigo = str(
            data.get("codigo", "")
        ).strip()

        installation_id = str(
            data.get("installation_id", "")
        ).strip()

        version_app = str(
            data.get("version_app", "")
        ).strip()

        licencia, dispositivo = validar_licencia(
            codigo=codigo,
            installation_id=installation_id,
            version_app=version_app,
        )

        licencia_firmada = firmar_licencia(
            licencia,
            dispositivo,
        )

        return JsonResponse(
            {
                "ok": True,
                "mensaje": "Licencia válida.",
                "licencia": {
                    "codigo": licencia.codigo,
                    "estado": licencia.estado_efectivo,
                    "cliente": str(licencia.cliente),
                    "fecha_activacion": (
                        licencia.fecha_activacion.isoformat()
                        if licencia.fecha_activacion
                        else None
                    ),
                    "fecha_vencimiento": (
                        licencia.fecha_vencimiento.isoformat()
                        if licencia.fecha_vencimiento
                        else None
                    ),
                },
                "dispositivo": {
                    "installation_id": dispositivo.installation_id,
                    "nombre": dispositivo.nombre_dispositivo,
                    "plataforma": dispositivo.plataforma,
                    "version_app": dispositivo.version_app,
                },
                "licencia_firmada": licencia_firmada,
            },
            status=200,
        )

    except ErrorValidacion as error:
        return JsonResponse(
            {
                "ok": False,
                "mensaje": str(error),
            },
            status=400,
        )

    except Exception:
        return JsonResponse(
            {
                "ok": False,
                "mensaje": "Ocurrió un error interno al validar la licencia.",
            },
            status=500,
        )
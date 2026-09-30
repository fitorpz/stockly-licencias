import secrets
import string

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

from .models import Activacion, Dispositivo, Licencia, Renovacion

ALFABETO_CODIGO = string.ascii_uppercase + string.digits


def _generar_bloque(longitud=4):
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(longitud))


def generar_codigo_licencia():
    """
    Genera códigos como:

    STK-A7F2-K9P4-X2M8
    """

    for _ in range(20):
        codigo = "STK-" + "-".join(_generar_bloque() for _ in range(3))

        if not Licencia.objects.filter(codigo=codigo).exists():
            return codigo

    raise RuntimeError("No fue posible generar un código de licencia único.")


@transaction.atomic
def crear_licencia(
    *,
    cliente,
    creditos,
    bonificacion,
    usuario,
    observaciones="",
):
    codigo = generar_codigo_licencia()

    licencia = Licencia.objects.create(
        codigo=codigo,
        cliente=cliente,
        creditos=creditos,
        bonificacion=bonificacion,
        estado=Licencia.Estado.PENDIENTE,
        observaciones=observaciones,
        creado_por=usuario,
    )

    return licencia
class ErrorActivacion(Exception):
    pass


def _obtener_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


@transaction.atomic
def activar_licencia(
    *,
    codigo,
    installation_id,
    version_app="",
    nombre_dispositivo="",
    plataforma="",
    request=None,
):
    codigo = codigo.strip().upper()
    installation_id = installation_id.strip()

    if not codigo:
        raise ErrorActivacion("Debe proporcionar el código de licencia.")

    if not installation_id:
        raise ErrorActivacion("Debe proporcionar el identificador de instalación.")

    try:
        licencia = (
            Licencia.objects.select_for_update()
            .select_related("cliente")
            .get(codigo=codigo)
        )
    except Licencia.DoesNotExist:
        raise ErrorActivacion("El código de licencia no existe.")

    if licencia.estado == Licencia.Estado.BLOQUEADA:
        raise ErrorActivacion("La licencia se encuentra bloqueada.")

    if licencia.estado == Licencia.Estado.CANCELADA:
        raise ErrorActivacion("La licencia se encuentra cancelada.")

    dispositivo_existente = (
        Dispositivo.objects.select_for_update()
        .filter(installation_id=installation_id)
        .first()
    )

    if dispositivo_existente and dispositivo_existente.licencia_id != licencia.id:
        raise ErrorActivacion("Este dispositivo ya está asociado a otra licencia.")

    dispositivo_licencia = (
        licencia.dispositivos.filter(activo=True)
        .exclude(installation_id=installation_id)
        .first()
    )

    if dispositivo_licencia:
        raise ErrorActivacion("La licencia ya está vinculada a otro dispositivo.")

    ahora = timezone.now()

    if licencia.estado == Licencia.Estado.PENDIENTE:

        meses = licencia.meses_vigencia

        licencia.estado = Licencia.Estado.ACTIVA
        licencia.fecha_activacion = ahora
        licencia.fecha_vencimiento = ahora + relativedelta(months=meses)

        licencia.save(
            update_fields=[
                "estado",
                "fecha_activacion",
                "fecha_vencimiento",
                "actualizado_en",
            ]
        )

    elif licencia.estado == Licencia.Estado.ACTIVA:

        if licencia.esta_vencida:
            raise ErrorActivacion("La licencia se encuentra vencida.")

    else:
        raise ErrorActivacion("La licencia no puede ser activada.")

    if dispositivo_existente:
        dispositivo = dispositivo_existente

        dispositivo.nombre_dispositivo = (
            nombre_dispositivo or dispositivo.nombre_dispositivo
        )

        dispositivo.version_app = version_app

        if plataforma:
            dispositivo.plataforma = plataforma

        dispositivo.ultima_actividad = ahora
        dispositivo.activo = True

        dispositivo.save(
            update_fields=[
                "nombre_dispositivo",
                "plataforma",
                "version_app",
                "ultima_actividad",
                "activo",
            ]
        )

    else:
        dispositivo = Dispositivo.objects.create(
            licencia=licencia,
            installation_id=installation_id,
            nombre_dispositivo=nombre_dispositivo,
            plataforma=plataforma,
            version_app=version_app,
            activo=True,
            ultima_actividad=ahora,
        )

    Activacion.objects.create(
        licencia=licencia,
        dispositivo=dispositivo,
        ip=_obtener_ip(request) if request else None,
        version_app=version_app,
        exitosa=True,
        mensaje="Licencia validada correctamente.",
    )

    return licencia, dispositivo

@transaction.atomic
def renovar_licencia(
    *,
    licencia,
    creditos,
    bonificacion,
    monto,
    usuario,
    observaciones="",
):
    licencia = (
        Licencia.objects
        .select_for_update()
        .get(pk=licencia.pk)
    )

    if licencia.estado in (
        Licencia.Estado.BLOQUEADA,
        Licencia.Estado.CANCELADA,
    ):
        raise ValueError(
            "No se puede renovar una licencia bloqueada o cancelada."
        )

    ahora = timezone.now()

    vencimiento_anterior = licencia.fecha_vencimiento

    if (
        vencimiento_anterior
        and vencimiento_anterior > ahora
    ):
        fecha_base = vencimiento_anterior
    else:
        fecha_base = ahora

    meses = creditos + bonificacion

    nuevo_vencimiento = (
        fecha_base + relativedelta(months=meses)
    )

    licencia.creditos += creditos
    licencia.bonificacion += bonificacion
    licencia.fecha_vencimiento = nuevo_vencimiento

    if licencia.fecha_activacion is None:
        licencia.fecha_activacion = ahora

    licencia.estado = Licencia.Estado.ACTIVA

    licencia.save(
        update_fields=[
            "creditos",
            "bonificacion",
            "fecha_activacion",
            "fecha_vencimiento",
            "estado",
            "actualizado_en",
        ]
    )

    Renovacion.objects.create(
        licencia=licencia,
        creditos=creditos,
        bonificacion=bonificacion,
        vencimiento_anterior=vencimiento_anterior,
        nuevo_vencimiento=nuevo_vencimiento,
        monto=monto,
        observaciones=observaciones,
        creado_por=usuario,
    )

    return licencia

class ErrorValidacion(Exception):
    pass


@transaction.atomic
def validar_licencia(
    *,
    codigo,
    installation_id,
    version_app="",
):
    codigo = codigo.strip().upper()
    installation_id = installation_id.strip()

    if not codigo:
        raise ErrorValidacion(
            "Debe proporcionar el código de licencia."
        )

    if not installation_id:
        raise ErrorValidacion(
            "Debe proporcionar el identificador de instalación."
        )

    try:
        licencia = (
            Licencia.objects
            .select_for_update()
            .select_related("cliente")
            .get(codigo=codigo)
        )

    except Licencia.DoesNotExist:
        raise ErrorValidacion(
            "El código de licencia no existe."
        )

    if licencia.estado == Licencia.Estado.PENDIENTE:
        raise ErrorValidacion(
            "La licencia todavía no fue activada."
        )

    if licencia.estado == Licencia.Estado.BLOQUEADA:
        raise ErrorValidacion(
            "La licencia se encuentra bloqueada."
        )

    if licencia.estado == Licencia.Estado.CANCELADA:
        raise ErrorValidacion(
            "La licencia se encuentra cancelada."
        )

    if licencia.estado != Licencia.Estado.ACTIVA:
        raise ErrorValidacion(
            "La licencia no se encuentra activa."
        )

    if licencia.esta_vencida:
        raise ErrorValidacion(
            "La licencia se encuentra vencida."
        )

    try:
        dispositivo = (
            Dispositivo.objects
            .select_for_update()
            .get(
                licencia=licencia,
                installation_id=installation_id,
            )
        )

    except Dispositivo.DoesNotExist:
        raise ErrorValidacion(
            "Este dispositivo no está autorizado para utilizar la licencia."
        )

    if not dispositivo.activo:
        raise ErrorValidacion(
            "Este dispositivo se encuentra deshabilitado."
        )

    dispositivo.ultima_actividad = timezone.now()

    if version_app:
        dispositivo.version_app = version_app

    dispositivo.save(
        update_fields=[
            "ultima_actividad",
            "version_app",
        ]
    )

    return licencia, dispositivo

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from clientes.models import Cliente


class Plan(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
    )
    creditos = models.PositiveSmallIntegerField(
        help_text="1 crédito equivale a 1 mes de licencia."
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    activo = models.BooleanField(
        default=True,
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
    )

    @property
    def meses_vigencia(self):
        return self.creditos

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["creditos"]


class Licencia(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACTIVA = "ACTIVA", "Activa"
        BLOQUEDA = "BLOQUEADA", "Bloqueada"
        CANCELADA = "CANCELADA", "Cancelada"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    codigo = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="licencias",
    )
    creditos = models.PositiveSmallIntegerField(
        default=1,
        help_text="Cantidad de meses otorgados. 1 crédito equivale a 1 mes.",
    )
    bonificacion = models.PositiveSmallIntegerField(
        default=0,
        help_text="Meses adicionales otorgados sin costo.",
    )
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )
    fecha_activacion = models.DateTimeField(
        null=True,
        blank=True,
    )
    fecha_vencimiento = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )
    observaciones = models.TextField(
        blank=True,
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="licencias_creadas",
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
    )

    @property
    def meses_vigencia(self):
        return self.creditos + self.bonificacion

    @property
    def esta_vencida(self):
        if not self.fecha_vencimiento:
            return False

        return self.fecha_vencimiento <= timezone.now()

    @property
    def estado_efectivo(self):
        if self.estado == self.Estado.ACTIVA and self.esta_vencida:
            return "VENCIDA"

        return self.estado

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"
        ordering = ["-fecha_creacion"]


class Dispositivo(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    licencia = models.ForeignKey(
        Licencia,
        on_delete=models.PROTECT,
        related_name="dispositivos",
    )
    installation_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )
    nombre_dispositivo = models.CharField(
        max_length=150,
        blank=True,
    )
    plataforma = models.CharField(
        max_length=150,
        blank=True,
    )
    version_app = models.CharField(
        max_length=50,
        blank=True,
    )
    activo = models.BooleanField(
        default=True,
    )
    primera_activacion = models.DateField(
        auto_now_add=True,
    )
    ultima_actividad = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.nombre_dispositivo or self.installation_id

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ["-primera_activacion"]


class Activacion(models.Model):
    licencia = models.ForeignKey(
        Licencia,
        on_delete=models.PROTECT,
        related_name="activaciones",
    )
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.PROTECT,
        related_name="activaciones",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
    )
    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    version_app = models.CharField(
        max_length=50,
        blank=True,
    )
    exitosa = models.BooleanField(
        default=True,
    )
    mensaje = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.licencia.codigo} - {self.fecha}"

    class Meta:
        verbose_name = "Activacion"
        verbose_name_plural = "activaciones"
        ordering = ["-fecha"]


class Renovacion(models.Model):
    licencia = models.ForeignKey(
        Licencia,
        on_delete=models.PROTECT,
        related_name="renovaciones",
    )

    creditos = models.PositiveSmallIntegerField(default=1)
    bonificacion = models.PositiveSmallIntegerField(default=0)

    fecha = models.DateTimeField(auto_now_add=True)

    vencimiento_anterior = models.DateTimeField(
        null=True,
        blank=True,
    )

    nuevo_vencimiento = models.DateTimeField()

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    observaciones = models.TextField(blank=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="renovaciones_creadas",
    )

    @property
    def meses_otorgados(self):
        return self.creditos + self.bonificacion

    def __str__(self):
        return f"{self.licencia.codigo} - {self.nuevo_vencimiento}"

    class Meta:
        verbose_name = "Renovación"
        verbose_name_plural = "Renovaciones"
        ordering = ["-fecha"]
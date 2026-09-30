from django.db import models


class Cliente(models.Model):
    class TipoCliente(models.TextChoices):
        PERSONA = "PERSONA", "Persona"
        EMPRESA = "EMPRESA", "Empresa"

    tipo = models.CharField(
        max_length=20,
        choices=TipoCliente.choices,
        default=TipoCliente.EMPRESA,
    )

    nombre = models.CharField(
        max_length=150,
    )
    razon_social = models.CharField(
        max_length=50,
        blank=True,
    )
    nit_documento = models.CharField(
        max_length=50,
        blank=True,
    )
    telefono = models.CharField(
        max_length=50,
        blank=True,
    )
    email = models.EmailField(
        blank=True,
    )
    direccion = models.CharField(
        max_length=255,
        blank=True,
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
    )
    observaciones = models.TextField(
        default=True,
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

    def __str__(self):
        return self.razon_social or self.nombre

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

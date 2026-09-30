from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

        fields = (
            "tipo",
            "nombre",
            "razon_social",
            "nit_documento",
            "telefono",
            "email",
            "direccion",
            "ciudad",
            "observaciones",
            "activo",
        )

        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del cliente",
                }
            ),
            "razon_social": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Razón social",
                }
            ),
            "nit_documento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "NIT o documento",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Teléfono",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Correo electrónico",
                }
            ),
            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección",
                }
            ),
            "ciudad": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ciudad",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones",
                }
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

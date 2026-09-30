from django import forms

from clientes.models import Cliente

from .models import Licencia, Renovacion

class LicenciaForm(forms.ModelForm):
    class Meta:
        model = Licencia
        fields = (
            "cliente",
            "creditos",
            "bonificacion",
            "observaciones",
        )

        widgets = {
            "cliente": forms.Select(
                attrs={"class": "form-select"}
            ),
            "creditos": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "1",
                }
            ),
            "bonificacion": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "1",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones de la licencia",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cliente"].queryset = (
            Cliente.objects
            .filter(activo=True)
            .order_by("nombre")
        )

        self.fields["cliente"].empty_label = "Seleccione un cliente"

        self.fields["creditos"].label = "Créditos"
        self.fields["bonificacion"].label = "Bonificación"

    def clean_creditos(self):
        creditos = self.cleaned_data["creditos"]

        if creditos < 1:
            raise forms.ValidationError(
                "Debe asignar al menos 1 crédito."
            )

        return creditos

class RenovacionForm(forms.ModelForm):
    class Meta:
        model = Renovacion

        fields = (
            "creditos",
            "bonificacion",
            "monto",
            "observaciones",
        )

        widgets = {
            "creditos": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "1",
                }
            ),
            "bonificacion": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "1",
                }
            ),
            "monto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def clean_creditos(self):
        creditos = self.cleaned_data["creditos"]

        if creditos < 1:
            raise forms.ValidationError(
                "Debe asignar al menos 1 crédito."
            )

        return creditos
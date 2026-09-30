from django import forms
from django.contrib.auth.models import User


class UsuarioCrearForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
        ]

        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_staff": "Administrador",
            "is_active": "Activo",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "is_staff": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "Ya existe un usuario con este nombre."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Ya existe un usuario con este correo electrónico."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error(
                "password2",
                "Las contraseñas no coinciden.",
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password1"]
        )

        if commit:
            user.save()

        return user


class UsuarioEditarForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
        ]

        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_staff": "Administrador",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "is_staff": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        existe = User.objects.filter(
            username__iexact=username,
        ).exclude(
            pk=self.instance.pk,
        ).exists()

        if existe:
            raise forms.ValidationError(
                "Ya existe otro usuario con este nombre."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        if not email:
            return email

        existe = User.objects.filter(
            email__iexact=email,
        ).exclude(
            pk=self.instance.pk,
        ).exists()

        if existe:
            raise forms.ValidationError(
                "Ya existe otro usuario con este correo electrónico."
            )

        return email


class UsuarioPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error(
                "password2",
                "Las contraseñas no coinciden.",
            )

        return cleaned_data
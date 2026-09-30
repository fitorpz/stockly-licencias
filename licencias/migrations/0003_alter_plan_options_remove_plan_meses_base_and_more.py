from django.db import migrations, models


def copiar_meses_a_creditos(apps, schema_editor):
    Plan = apps.get_model("licencias", "Plan")

    for plan in Plan.objects.all():
        plan.creditos = plan.meses_base
        plan.save(update_fields=["creditos"])


class Migration(migrations.Migration):

    dependencies = [
        ("licencias", "0002_rename_observcacion_licencia_observaciones"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="creditos",
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text="1 crédito equivale a 1 mes de licencia.",
            ),
        ),

        migrations.RunPython(
            copiar_meses_a_creditos,
            migrations.RunPython.noop,
        ),

        migrations.RemoveField(
            model_name="plan",
            name="meses_base",
        ),

        migrations.RemoveField(
            model_name="plan",
            name="meses_bonificacion",
        ),

        migrations.AlterModelOptions(
            name="plan",
            options={
                "ordering": ["creditos"],
                "verbose_name": "Plan",
                "verbose_name_plural": "Planes",
            },
        ),
    ]
from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.ChAutorizacao)
admin.site.register(models.ChArquivo)
admin.site.register(models.ChCategoria)
admin.site.register(models.ChChamado)
admin.site.register(models.ChInteracao)
admin.site.register(models.ChServicos)
admin.site.register(models.ChStatus)
admin.site.register(models.ChSubcategoria)
admin.site.register(models.UsuGrupoUsuario)
admin.site.register(models.UsuSetor)
admin.site.register(models.UsuUnidade)
admin.site.register(models.UsuUsuario)
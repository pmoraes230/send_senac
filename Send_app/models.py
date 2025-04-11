from django.db import models


class ChArquivo(models.Model):
    id_interacao = models.ForeignKey('ChInteracao', models.DO_NOTHING, db_column='id_interacao')
    arquivo = models.CharField(max_length=200, blank=True, null=True)
    extensao = models.CharField(max_length=5, blank=True, null=True)
    tamanho = models.FloatField(blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_arquivo'

    def __str__(self):
        return self.arquivo


class ChAutorizacao(models.Model):
    ch_chamado = models.ForeignKey('ChChamado', models.DO_NOTHING)
    usu_usuario = models.ForeignKey('UsuUsuario', models.DO_NOTHING)
    parecer = models.TextField(blank=True, null=True)
    data_autorizacao = models.DateTimeField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_autorizacao'
    
    def __str__(self):
        return self.usu_usuario


class ChCategoria(models.Model):
    id_grupo_usuario = models.ForeignKey('UsuGrupoUsuario', models.DO_NOTHING, db_column='id_grupo_usuario')
    id_setor = models.ForeignKey('UsuSetor', models.DO_NOTHING, db_column='id_setor')
    nome = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    ativo = models.IntegerField(blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_categoria'
    
    def __str__(self):
        return self.nome


class ChCategoriaDoChamado(models.Model):
    pk = models.CompositePrimaryKey('id_chamado', 'id_subcategoria')
    id_chamado = models.ForeignKey('ChChamado', models.DO_NOTHING, db_column='id_chamado')
    id_subcategoria = models.ForeignKey('ChSubcategoria', models.DO_NOTHING, db_column='id_subcategoria')
    id_categoria = models.ForeignKey(ChCategoria, models.DO_NOTHING, db_column='id_categoria')

    class Meta:
        managed = False
        db_table = 'ch_categoria_do_chamado'
        unique_together = (('id_chamado', 'id_subcategoria'),)


class ChChamado(models.Model):
    id_usuario = models.ForeignKey('UsuUsuario', models.DO_NOTHING, db_column='id_usuario')
    id_setor = models.ForeignKey('UsuSetor', models.DO_NOTHING, db_column='id_setor')
    id_unidade = models.ForeignKey('UsuUnidade', models.DO_NOTHING, db_column='id_unidade')
    id_usuario_suporte = models.ForeignKey('UsuUsuario', models.DO_NOTHING, db_column='id_usuario_suporte', related_name='chchamado_id_usuario_suporte_set')
    id_setor_suporte = models.ForeignKey('UsuSetor', models.DO_NOTHING, db_column='id_setor_suporte', related_name='chchamado_id_setor_suporte_set')
    id_status = models.ForeignKey('ChStatus', models.DO_NOTHING, db_column='id_status')
    prioridade = models.IntegerField(blank=True, null=True)
    patrimonio = models.IntegerField(blank=True, null=True)
    data_inicio_suporte = models.DateTimeField(blank=True, null=True)
    data_encerramento = models.DateTimeField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_chamado'

    def __str__(self):
        return self.descricao


class ChInteracao(models.Model):
    id_usuario = models.ForeignKey('UsuUsuario', models.DO_NOTHING, db_column='id_usuario')
    id_chamado = models.ForeignKey(ChChamado, models.DO_NOTHING, db_column='id_chamado')
    id_status = models.ForeignKey('ChStatus', models.DO_NOTHING, db_column='id_status')
    descricao = models.TextField(blank=True, null=True)
    suporte = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_interacao'

    def __str__(self):
        return self.descricao


class ChServicos(models.Model):
    id_subcategoria = models.ForeignKey('ChSubcategoria', models.DO_NOTHING, db_column='id_subcategoria')
    nome = models.CharField(max_length=255, blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_servicos'
    
    def __str__(self):
        return self.nome
    
    
class ChServicosChamado(models.Model):
    pk = models.CompositePrimaryKey('id_servicos', 'id_chamado')
    id_servicos = models.ForeignKey(ChServicos, models.DO_NOTHING, db_column='id_servicos')
    id_chamado = models.ForeignKey(ChChamado, models.DO_NOTHING, db_column='id_chamado')
    id_usuario_suporte = models.ForeignKey('UsuUsuario', models.DO_NOTHING, db_column='id_usuario_suporte')
    data_conclusao = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_servicos_chamado'
        unique_together = (('id_servicos', 'id_chamado'),)


class ChStatus(models.Model):
    nome = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_status'
    
    def __str__(self):
        return self.nome


class ChSubcategoria(models.Model):
    id_grupo_usuario = models.ForeignKey('UsuGrupoUsuario', models.DO_NOTHING, db_column='id_grupo_usuario')
    id_categoria = models.ForeignKey(ChCategoria, models.DO_NOTHING, db_column='id_categoria')
    nome = models.CharField(max_length=100, blank=True, null=True)
    prioridade = models.IntegerField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    autorizacao = models.IntegerField(blank=True, null=True)
    ativo = models.IntegerField(blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ch_subcategoria'
    
    def __str__(self):
        return self.nome


class UsuGrupoUsuario(models.Model):
    nome = models.CharField(max_length=45, blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usu_grupo_usuario'

    def __str__(self):
        return self.nome


class UsuSetor(models.Model):
    nome = models.CharField(max_length=100, blank=True, null=True)
    suporte = models.IntegerField(blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usu_setor'

    def __str__(self):
        return self.nome


class UsuUnidade(models.Model):
    nome = models.CharField(max_length=100, blank=True, null=True)
    deletado = models.IntegerField(blank=True, null=True)
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usu_unidade'

    def __str__(self):
        return self.nome


class UsuUsuario(models.Model):
    id_grupo_usuario = models.ForeignKey(UsuGrupoUsuario, models.DO_NOTHING, db_column='id_grupo_usuario')
    id_setor = models.ForeignKey(UsuSetor, models.DO_NOTHING, db_column='id_setor', blank=True, null=True)
    id_unidade = models.ForeignKey(UsuUnidade, models.DO_NOTHING, db_column='id_unidade', blank=True, null=True)
    nome = models.CharField(max_length=200, blank=True, null=True)
    nome_exibicao = models.CharField(max_length=255, blank=True, null=True)
    login = models.CharField(max_length=100, blank=True, null=True)
    senha = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    email_institucional = models.CharField(max_length=100, blank=True, null=True)
    ativo = models.IntegerField(blank=True, null=True)
    deletado = models.BooleanField()
    data_cadastro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usu_usuario'

    def __str__(self):
        return self.nome

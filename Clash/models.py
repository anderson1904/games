from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
import uuid
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os
#__________________________________________
#|                                        |
#|           funções auxiliares           |
#|________________________________________|

# Função para o campo Foto_Jogador
def gerar_caminho_foto_jogador(instance, filename):
    extensao = filename.split('.')[-1]
    nome_arquivo = f'{uuid.uuid4()}.{extensao}'
    return f'fotos_jogador/{nome_arquivo}'

# Função para o campo Foto_Perfil
def gerar_caminho_foto_perfil(instance, filename):
    extensao = filename.split('.')[-1]
    nome_arquivo = f'{uuid.uuid4()}.{extensao}'
    return f'fotos_perfil/{nome_arquivo}'

# Função para o campo Foto_Produto
def gerar_caminho_imagem_produto(instance, filename):
    extensao = filename.split('.')[-1]
    nome_arquivo = f'{uuid.uuid4()}.{extensao}'
    return f'fotos_produtos/{nome_arquivo}'

#_______________________________________________
#|                                             |
#|        as tabelas do banco de dados         |
#|_____________________________________________|

#relativos a usuários e autenticação
# Modelo customizado de usuário que herda de AbstractUser.
class tbUser(AbstractUser):
    Data_Nascimento = models.DateField(null=True, blank=True)
    Foto_Perfil = models.ImageField(
        upload_to=gerar_caminho_foto_perfil,
        null=True,
        blank=True,
    )
    # Propriedade que calcula a idade com base na Data_Nascimento.
    @property
    def idade(self):
        if self.Data_Nascimento:
            hoje = date.today()
            return hoje.year - self.Data_Nascimento.year - (
                (hoje.month, hoje.day) < (self.Data_Nascimento.month, self.Data_Nascimento.day)
            )
        return None

class tbCartao(models.Model):
    Tipo_Cartao = models.CharField(max_length = 50)
    Numero_Cartao = models.CharField(max_length = 16)
    Nome_Cartao = models.CharField(max_length = 100)

class tbJogador(models.Model):
    Nome = models.CharField(max_length = 100)
    Nickname = models.CharField(max_length = 50)
    Data_Nascimento = models.DateField(null = True, blank = True)
    sobre = models.TextField()
    trofeus = models.IntegerField(default = 0)
    Foto_Jogador = models.ImageField(
        upload_to = gerar_caminho_foto_jogador, 
        null = True,
        blank = True,
    )
    @property
    def idade(self):
        if self.Data_Nascimento:
            hoje = date.today()
            return hoje.year - self.Data_Nascimento.year - (
                (hoje.month, hoje.day) < (self.Data_Nascimento.month, self.Data_Nascimento.day)
            )
        return None
    
    def __str__(self):
        return self.Nickname

def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)

@receiver(post_delete, sender=tbUser)
@receiver(post_delete, sender=tbJogador)
def delete_image_on_delete(sender, instance, **kwargs):
    # Verifica tbUser
    if sender == tbUser and instance.Foto_Perfil:
        _delete_file(instance.Foto_Perfil.path)
    
    # Verifica tbJogador
    if sender == tbJogador and instance.Foto_Jogador:
        _delete_file(instance.Foto_Jogador.path)

@receiver(pre_save, sender=tbUser)
@receiver(pre_save, sender=tbJogador)
def delete_old_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False
    # Lógica para tbUser
    if sender == tbUser:
        try:
            old_file = old_instance.Foto_Perfil
            new_file = instance.Foto_Perfil
            if old_file and old_file != new_file:
                _delete_file(old_file.path)
        except ValueError:
            pass

    # Lógica para tbJogador
    if sender == tbJogador:
        try:
            old_file = old_instance.Foto_Jogador
            new_file = instance.Foto_Jogador
            if old_file and old_file != new_file:
                _delete_file(old_file.path)
        except ValueError:
            pass

#relativos a conteúdo e entretenimento
class tbPartida(models.Model):
    Data_Prevista = models.DateTimeField()
    Time_Adversario = models.CharField(max_length = 100)
    Modalidade = models.CharField(max_length = 50)

class tbJogador_Partida(models.Model):
    tbJogador = models.ForeignKey(tbJogador, on_delete=models.CASCADE)
    tbPartida = models.ForeignKey(tbPartida, on_delete=models.CASCADE)

class tbStream(models.Model):
    partida = models.ForeignKey(
        tbPartida, 
        on_delete=models.CASCADE,
        related_name='transmissoes',
    )
    tipo = models.CharField(max_length=50)
    embed = models.TextField()

    class Meta:
        verbose_name = "Transmissão"
        verbose_name_plural = "Transmissões"

    def __str__(self):
        return f"Transmissão de '{self.partida.nome}' via {self.tipo}"

class tbNoticia(models.Model):
    Titulo = models.CharField(max_length=100)
    TextoHTML = models.TextField()
    Partida = models.ForeignKey(
        tbPartida,
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
    )

class tbEdita(models.Model):
    Data_Edicao = models.DateField(auto_now_add=True)
    tbUser = models.ForeignKey(tbUser, on_delete=models.CASCADE)
    tbNoticia = models.ForeignKey('tbNoticia', on_delete=models.CASCADE)

#relativos a compras e vendas
class tbCarrinho(models.Model):
    User = models.ForeignKey(tbUser, on_delete=models.CASCADE)
    Preco_Total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )

class tbProduto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=100, blank=True)
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    especificacoes = models.ManyToManyField(
        'tbFoto', 
        through='tbEspecifica', 
        related_name='produtos_especificados',
    )
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
    def __str__(self):
        return self.nome

class tbFoto(models.Model):
    produto = models.ForeignKey(
        tbProduto, 
        on_delete=models.CASCADE, 
        related_name='Foto',
    )
    foto = models.ImageField(
        upload_to=gerar_caminho_imagem_produto,
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name = "Foto"
        verbose_name_plural = "Fotos"
    def __str__(self):
        return f"Foto de {self.produto.nome}"

class tbTipoEspecificacao(models.Model):
    nome = models.CharField(max_length=50) # Ex: "Cor", "Tamanho"
    def __str__(self):
        return self.nome

class tbEspecifica(models.Model):
    produto = models.ForeignKey(tbProduto, on_delete=models.CASCADE)
    foto = models.ForeignKey(tbFoto, on_delete=models.CASCADE)
    tipo = models.ForeignKey(tbTipoEspecificacao, on_delete=models.CASCADE, null=True)
    descricao = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('produto', 'foto')
        verbose_name = "Especificação"
        verbose_name_plural = "Especificações"
    def __str__(self):
        return f"Especificação de {self.produto.nome} com a foto ID {self.foto.id}"

class tbCompra(models.Model):
    carrinho = models.ForeignKey(
        tbCarrinho, 
        on_delete=models.CASCADE, 
        related_name='itens',
    )
    produto = models.ForeignKey(
        tbProduto, 
        on_delete=models.CASCADE,
    )
    especificacoes = models.ManyToManyField(tbEspecifica, blank=True)
    quantidade = models.PositiveIntegerField(default=1)
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2) 
    frete = models.DecimalField(
        max_digits = 10, 
        decimal_places = 2, 
        default = 0
    )
    @property
    def valor_total(self):
        return (self.valor_compra * self.quantidade) + self.frete
    class Meta:
        verbose_name = "Item de Compra"
        verbose_name_plural = "Itens de Compra"
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} no Carrinho {self.carrinho.id}"

class tbPedido(models.Model):
    STATUS_CHOICES = (
        ('Pendente', 'Pendente'),
        ('Aprovado', 'Aprovado'),
        ('Enviado', 'Enviado'),
        ('Entregue', 'Entregue'),
        ('Cancelado', 'Cancelado'),
    )
    user = models.ForeignKey(tbUser, on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} de {self.user.username}"

class tbItemPedido(models.Model):
    pedido = models.ForeignKey(tbPedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(tbProduto, on_delete=models.SET_NULL, null=True) # Se o produto for deletado, o histórico permanece
    # Copiamos o nome do produto caso ele seja deletado futuramente
    nome_produto = models.CharField(max_length=255) 
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    # Como as especificações podem mudar, podemos salvar como texto para histórico simples
    especificacoes_texto = models.TextField(blank=True, null=True) 

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f"{self.quantidade}x {self.nome_produto} (Pedido #{self.pedido.id})"
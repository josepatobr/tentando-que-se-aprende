from django.shortcuts import render, redirect
from .models import Empresas, Documentos, Metricas
from investidores.models import PropostaInvestimento
from django.contrib import messages
from django.contrib.messages import constants


def cadastrar_empresa(request):
    if not request.user.is_authenticated:
        return redirect("logar")

    if request.method == "GET":
        return render(request,"cadastrar_empresa.html",{
                "tempo_existencia": Empresas.tempo_existencia_choices,
                "areas": Empresas.area_choices,
            },
        )

    elif request.method == "POST":
        nome = request.POST.get("nome")
        cnpj = request.POST.get("cnpj")
        site = request.POST.get("site")
        tempo_existencia = request.POST.get("tempo_existencia")
        descricao = request.POST.get("descricao")
        data_final = request.POST.get("data_final")
        percentual_equity = request.POST.get("percentual_equity")
        estagio = request.POST.get("estagio")
        area = request.POST.get("area")
        publico_alvo = request.POST.get("publico_alvo")
        valor = request.POST.get("valor")
        pitch = request.FILES.get("pitch")
        logo = request.FILES.get("logo")

    try:
        empresa = Empresas(
            user=request.user,
            nome=nome,
            cnpj=cnpj,
            site=site,
            tempo_existencia=tempo_existencia,
            descricao=descricao,
            data_final_captacao=data_final,
            percentual_equity=percentual_equity,
            estagio=estagio,
            area=area,
            publico_alvo=publico_alvo,
            valor=valor,
            pitch=pitch,
            logo=logo,
        )
        empresa.save()
    except Exception:
        messages.add_message(request, constants.ERROR, "Erro no sistema")
        return redirect("/empresarios/cadastrar_empresa")
    messages.add_message(request, constants.SUCCESS, "Empresa criada com sucesso")
    return redirect("/empresarios/cadastrar_empresa")


def listar_empresas(request):
    if not request.user.is_authenticated:
        return redirect("logar")

    if request.method == "GET":
        empresas = Empresas.objects.filter(user=request.user)
        return render(request, "listar_empresas.html", {"empresas": empresas})


def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    if request.method == "GET":
        documentos =  Documentos.objects.filter(empresa=empresa)
        propostas_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
        percentual_vendido = 0
        for pi in propostas_investimentos:
            if pi.status == 'PA':
                percentual_vendido = percentual_vendido + pi.percentual

        propostas_investimentos_enviados = propostas_investimentos.filter(status='PE')
        return render(request, "empresa.html", {"empresa": empresa, "documentos": documentos, 'propostas_investimentos_enviados':propostas_investimentos_enviados, 'percentual_vendido': int(percentual_vendido)})
    
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você enviou para uma empresa errada")
        return redirect (f'/empresario/listar_empresa')

def add_doc(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')
    
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você enviou para uma empresa errada")
        return redirect (f'/empresario/listar_empresa')

    if extensao[1] != 'pdf':
        messages.add_message(request, constants.ERROR, "O arquivo precisa ser em PDF")
        return redirect (f'/empresario/empresa/{id}')

    if not arquivo:
            messages.add_message(request, constants.ERROR, "Arquivo não pode ser vazio")
            return redirect (f'/empresario/empresa/{id}')

    documento = Documentos(
        empresa = empresa,
        titulo = titulo,
        arquivo = arquivo)
    documento.save() 
    messages.add_message(request, constants.SUCCESS, "Arquivo salvo")
    return redirect (f'/empresarios/empresa/{id}')

def excluir_dc(request, id):
    documento = Documentos.objects.get(id=id)
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    documento.delete()
    messages.add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')

def add_metrica(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')
    
    metrica = Metricas(
    empresa=empresa,
    titulo=titulo,
    valor=valor
    )
    metrica.save()
    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada')
        pi.status = 'PR'
    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')


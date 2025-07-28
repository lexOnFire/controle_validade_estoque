#!/usr/bin/env python3
"""
Script para converter arquivo FIFO CSV e consolidar registros duplicados
Versão melhorada para evitar conflitos de endereços e produtos duplicados
"""

import csv
import sys
from datetime import datetime
import re
from collections import defaultdict

def limpar_nome_produto(nome):
    """Limpa e normaliza nomes de produtos"""
    if not nome or nome is None:
        return ""
    
    nome = str(nome)
    nome = re.sub(r'[^\w\s\.\-\(\)]', ' ', nome)
    nome = ' '.join(nome.split())
    
    return nome.strip()

def processar_validade(validade_str):
    """Processa string de validade e converte para formato DD/MM/YYYY"""
    if not validade_str or validade_str.strip() == '':
        return None
    
    validade_str = validade_str.strip()
    
    # Verificar casos especiais que indicam ausência de validade
    casos_sem_validade = [
        's/ validade', 'sem validade', 'without expiry', 'no expiry',
        'n/a', 'na', 'null', 'none', 'vazio', 'empty', '-', '--'
    ]
    
    if validade_str.lower() in casos_sem_validade:
        return None
    
    # Se já está no formato DD/MM/YYYY, retorna como está
    if re.match(r'\d{2}/\d{2}/\d{4}', validade_str):
        return validade_str
    
    # Tenta outros formatos comuns
    formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
    
    for formato in formatos:
        try:
            data = datetime.strptime(validade_str, formato)
            return data.strftime('%d/%m/%Y')
        except ValueError:
            continue
    
    # Se não conseguiu converter, retorna None (sem validade)
    return None

def determinar_categoria(nome_produto):
    """Determina categoria baseada no nome do produto"""
    if not nome_produto or nome_produto is None:
        return 'Geral'
    
    nome_lower = str(nome_produto).lower()
    
    if 'vdc' in nome_lower or 'vdf' in nome_lower:
        return 'Veterinária'
    elif any(palavra in nome_lower for palavra in ['fhn', 'fbn', 'fcn']):
        return 'Alimentação'
    elif any(palavra in nome_lower for palavra in ['dental', 'care']):
        return 'Cuidados'
    else:
        return 'Geral'

def processar_tipo_palete(tipo_original, palete_original):
    """Processa informações de tipo e palete"""
    if not tipo_original and not palete_original:
        return 'AP', 'MEIO'
    
    tipo = tipo_original.strip() if tipo_original else 'AP'
    palete = palete_original.strip() if palete_original else 'MEIO'
    
    if palete.upper() in ['MEIO', 'INTEIRO']:
        palete = palete.upper()
    elif palete.upper() in ['TER O', 'TERCO', 'TERÇO']:
        palete = 'TERCO'
    else:
        palete = 'MEIO'
    
    return tipo, palete

def converter_fifo_consolidado(arquivo_origem, arquivo_destino):
    """
    Converte arquivo FIFO CSV consolidando registros duplicados
    """
    
    print(f"🔄 Processando arquivo: {arquivo_origem}")
    print(f"📄 Arquivo de saída: {arquivo_destino}")
    
    try:
        with open(arquivo_origem, 'r', encoding='utf-8-sig') as arquivo_entrada:
            primeira_linha = arquivo_entrada.readline()
            separador = ';' if primeira_linha.count(';') > primeira_linha.count(',') else ','
            
            arquivo_entrada.seek(0)
            reader = csv.DictReader(arquivo_entrada, delimiter=separador)
            
            print(f"📊 Colunas detectadas: {list(reader.fieldnames)}")
            print(f"🔍 Separador detectado: '{separador}'")
            
            # Dicionário para consolidar registros
            # Chave: (codigo, rua, predio, nivel, ap)
            # Valor: {dados do produto, lista de validades}
            registros_consolidados = defaultdict(lambda: {
                'produto': None,
                'validades': [],
                'datas_armazenado': set()
            })
            
            linha_atual = 1
            linhas_processadas = 0
            
            for row in reader:
                linha_atual += 1
                
                try:
                    # Extrair dados básicos
                    codigo = str(row.get('Cod.', row.get(' Cod.', ''))).strip()
                    nome = limpar_nome_produto(row.get('Produto', row.get(' Produto', '')))
                    rua = str(row.get('Rua', '')).strip()
                    predio = str(row.get('Pred', row.get(' Pred', ''))).strip()
                    nivel = str(row.get('Niv', row.get(' Niv', ''))).strip()
                    ap = str(row.get('Ap', row.get(' Ap', ''))).strip()
                    data_abastec = str(row.get('DATA ABASTEC.', row.get(' DATA ABASTEC.', ''))).strip()
                    
                    # Pular linhas sem dados essenciais
                    if not codigo or not nome or not rua or not predio:
                        continue
                    
                    # Processar tipo e palete
                    tipo_original = str(row.get('Tipo', row.get(' Tipo', ''))).strip()
                    palete_original = str(row.get('Palete ', row.get(' Palete ', ''))).strip()
                    tipo, palete = processar_tipo_palete(tipo_original, palete_original)
                    
                    # Determinar categoria
                    categoria = determinar_categoria(nome)
                    
                    # Chave única para consolidação
                    chave = (codigo, rua, predio, nivel, ap)
                    
                    # Se é a primeira vez que vemos esta combinação
                    if registros_consolidados[chave]['produto'] is None:
                        registros_consolidados[chave]['produto'] = {
                            'codigo': codigo,
                            'nome': nome,
                            'categoria': categoria,
                            'rua': rua,
                            'predio': predio,
                            'nivel': nivel,
                            'ap': ap,
                            'tipo': tipo,
                            'palete': palete
                        }
                    
                    # Adicionar data de armazenamento se disponível
                    if data_abastec:
                        registros_consolidados[chave]['datas_armazenado'].add(data_abastec)
                    
                    # Processar múltiplas validades
                    for i in range(1, 5):
                        val_col = f'VAL. {i}'
                        val_col_space = f' VAL. {i}'
                        
                        validade = None
                        if val_col in row:
                            validade = processar_validade(row[val_col])
                        elif val_col_space in row:
                            validade = processar_validade(row[val_col_space])
                        
                        if validade:
                            registros_consolidados[chave]['validades'].append(validade)
                    
                    linhas_processadas += 1
                        
                except Exception as e:
                    print(f"⚠️  Erro na linha {linha_atual}: {str(e)}")
                    continue
            
            # Agora gerar registros únicos consolidados
            registros_finais = []
            lote_counter = 1
            
            for chave, dados in registros_consolidados.items():
                produto = dados['produto']
                validades = list(set(dados['validades']))  # Remove duplicatas
                datas_armazenado = list(dados['datas_armazenado'])
                
                if not produto:
                    continue
                
                # Se não tem validades, criar um registro sem validade
                if not validades:
                    validades = [None]
                
                # Para cada validade única, criar um lote separado
                for i, validade in enumerate(validades):
                    # Usar a primeira data de armazenamento disponível
                    data_armazenado = datas_armazenado[0] if datas_armazenado else ''
                    
                    # Gerar número de lote único
                    numero_lote = f"L{lote_counter:04d}"
                    lote_counter += 1
                    
                    registro = {
                        'codigo': produto['codigo'],
                        'nome': produto['nome'],
                        'categoria': produto['categoria'],
                        'rua': produto['rua'],
                        'predio': produto['predio'],
                        'nivel': produto['nivel'],
                        'ap': produto['ap'],
                        'validade': validade if validade else '',
                        'data_armazenado': data_armazenado,
                        'quantidade': '1',
                        'numero_lote': numero_lote,
                        'tipo': produto['tipo'],
                        'palete': produto['palete']
                    }
                    
                    registros_finais.append(registro)
            
            # Escrever arquivo de saída
            with open(arquivo_destino, 'w', newline='', encoding='utf-8') as arquivo_saida:
                fieldnames = [
                    'codigo', 'nome', 'categoria', 'rua', 'predio', 'nivel', 'ap',
                    'validade', 'data_armazenado', 'quantidade', 'numero_lote', 'tipo', 'palete'
                ]
                
                writer = csv.DictWriter(arquivo_saida, fieldnames=fieldnames)
                writer.writeheader()
                
                for registro in registros_finais:
                    writer.writerow(registro)
            
            print(f"✅ Processamento consolidado concluído!")
            print(f"📈 {len(registros_finais)} registros únicos gerados")
            print(f"🔄 {linhas_processadas} linhas originais processadas")
            print(f"💾 Arquivo salvo em: {arquivo_destino}")
            
            # Estatísticas
            produtos_unicos = len(set(r['codigo'] for r in registros_finais))
            enderecos_unicos = len(set((r['rua'], r['predio'], r['nivel'], r['ap']) for r in registros_finais))
            registros_com_validade = len([r for r in registros_finais if r['validade']])
            
            print(f"📊 Estatísticas consolidadas:")
            print(f"   • Produtos únicos: {produtos_unicos}")
            print(f"   • Endereços únicos: {enderecos_unicos}")
            print(f"   • Registros com validade: {registros_com_validade}")
            print(f"   • Registros sem validade: {len(registros_finais) - registros_com_validade}")
            print(f"   • Lotes gerados: {lote_counter - 1}")
            
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo_origem}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante o processamento: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    arquivo_origem = r"c:\Users\alexs\Downloads\FIFO(ABASTECIMENTO 1).csv"
    arquivo_destino = r"c:\Users\alexs\controle_projeto\FIFO_CONSOLIDADO_FORMATADO.csv"
    
    print("🚀 Iniciando conversão consolidada de arquivo FIFO")
    print("🔧 Versão melhorada - evita registros duplicados")
    print("=" * 60)
    
    converter_fifo_consolidado(arquivo_origem, arquivo_destino)
    
    print("=" * 60)
    print("🎯 Arquivo consolidado pronto para importação!")
    print(f"   📁 Arquivo: {arquivo_destino}")
    print("   🌐 Acesse: http://127.0.0.1:8000/produtos/importar-abastecimento/")
    print("   📤 Faça upload do arquivo consolidado")
    print("   ✅ Sem erros de registros duplicados!")

#!/usr/bin/env python3
"""
Script para converter arquivo FIFO CSV para formato compatível com o sistema de controle de estoque
Desenvolvido para o projeto: controle_validade_estoque
"""

import csv
import sys
from datetime import datetime
import re

def limpar_nome_produto(nome):
    """Limpa e normaliza nomes de produtos"""
    if not nome or nome is None:
        return ""
    
    # Converte para string se não for
    nome = str(nome)
    
    # Remove caracteres especiais e normaliza espaços
    nome = re.sub(r'[^\w\s\.\-\(\)]', ' ', nome)
    nome = ' '.join(nome.split())  # Remove múltiplos espaços
    
    return nome.strip()

def processar_validade(validade_str):
    """Processa string de validade e converte para formato DD/MM/YYYY"""
    if not validade_str or validade_str.strip() == '':
        return None
    
    # Remove espaços extras
    validade_str = validade_str.strip()
    
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
    
    # Normaliza valores conhecidos
    if palete.upper() in ['MEIO', 'INTEIRO']:
        palete = palete.upper()
    elif palete.upper() in ['TER O', 'TERCO', 'TERÇO']:
        palete = 'TERCO'
    else:
        palete = 'MEIO'  # padrão
    
    return tipo, palete

def converter_fifo_para_sistema(arquivo_origem, arquivo_destino):
    """
    Converte arquivo FIFO CSV para formato do sistema
    """
    
    print(f"🔄 Processando arquivo: {arquivo_origem}")
    print(f"📄 Arquivo de saída: {arquivo_destino}")
    
    try:
        with open(arquivo_origem, 'r', encoding='utf-8-sig') as arquivo_entrada:
            # Detecta o separador
            primeira_linha = arquivo_entrada.readline()
            separador = ';' if primeira_linha.count(';') > primeira_linha.count(',') else ','
            
            # Volta ao início do arquivo
            arquivo_entrada.seek(0)
            
            # Lê com o separador correto
            reader = csv.DictReader(arquivo_entrada, delimiter=separador)
            
            print(f"📊 Colunas detectadas: {list(reader.fieldnames)}")
            print(f"🔍 Separador detectado: '{separador}'")
            
            registros_processados = []
            linha_atual = 1
            
            for row in reader:
                linha_atual += 1
                
                try:
                    # Extrair dados básicos - com tratamento para espaços nas colunas
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
                    
                    # Processar tipo e palete - com tratamento para espaços
                    tipo_original = str(row.get('Tipo', row.get(' Tipo', ''))).strip()
                    palete_original = str(row.get('Palete ', row.get(' Palete ', ''))).strip()  # Note o espaço extra
                    tipo, palete = processar_tipo_palete(tipo_original, palete_original)
                    
                    # Determinar categoria
                    categoria = determinar_categoria(nome)
                    
                    # Processar múltiplas validades (VAL. 1, VAL. 2, VAL. 3, VAL. 4)
                    validades = []
                    for i in range(1, 5):  # VAL. 1 a VAL. 4
                        # Tenta com e sem espaço inicial
                        val_col = f'VAL. {i}'
                        val_col_space = f' VAL. {i}'
                        
                        if val_col in row:
                            validade = processar_validade(row[val_col])
                            if validade:
                                validades.append(validade)
                        elif val_col_space in row:
                            validade = processar_validade(row[val_col_space])
                            if validade:
                                validades.append(validade)
                    
                    # Se não tem validades nas colunas VAL., tentar colunas individuais
                    if not validades:
                        for col_name in row.keys():
                            if 'val' in col_name.lower() and row[col_name]:
                                validade = processar_validade(row[col_name])
                                if validade:
                                    validades.append(validade)
                    
                    # Se ainda não tem validades, criar um registro sem validade
                    if not validades:
                        validades = [None]
                    
                    # Criar um registro para cada validade
                    for validade in validades:
                        registro = {
                            'codigo': codigo,
                            'nome': nome,
                            'categoria': categoria,
                            'rua': rua,
                            'predio': predio,
                            'nivel': nivel,
                            'ap': ap,
                            'validade': validade if validade else '',
                            'data_armazenado': data_abastec,
                            'quantidade': '1',  # padrão
                            'numero_lote': '',  # será gerado automaticamente
                            'tipo': tipo,
                            'palete': palete
                        }
                        
                        registros_processados.append(registro)
                        
                except Exception as e:
                    print(f"⚠️  Erro na linha {linha_atual}: {str(e)}")
                    continue
            
            # Escrever arquivo de saída
            with open(arquivo_destino, 'w', newline='', encoding='utf-8') as arquivo_saida:
                fieldnames = [
                    'codigo', 'nome', 'categoria', 'rua', 'predio', 'nivel', 'ap',
                    'validade', 'data_armazenado', 'quantidade', 'numero_lote', 'tipo', 'palete'
                ]
                
                writer = csv.DictWriter(arquivo_saida, fieldnames=fieldnames)
                writer.writeheader()
                
                for registro in registros_processados:
                    writer.writerow(registro)
            
            print(f"✅ Processamento concluído!")
            print(f"📈 {len(registros_processados)} registros processados")
            print(f"💾 Arquivo salvo em: {arquivo_destino}")
            
            # Estatísticas
            produtos_unicos = len(set(r['codigo'] for r in registros_processados))
            registros_com_validade = len([r for r in registros_processados if r['validade']])
            
            print(f"📊 Estatísticas:")
            print(f"   • Produtos únicos: {produtos_unicos}")
            print(f"   • Registros com validade: {registros_com_validade}")
            print(f"   • Registros sem validade: {len(registros_processados) - registros_com_validade}")
            
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo_origem}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro durante o processamento: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Arquivos de entrada e saída
    arquivo_origem = r"c:\Users\alexs\Downloads\FIFO(ABASTECIMENTO 1).csv"
    arquivo_destino = r"c:\Users\alexs\controle_projeto\FIFO_COMPLETO_FORMATADO.csv"
    
    print("🚀 Iniciando conversão de arquivo FIFO para sistema de estoque")
    print("=" * 60)
    
    converter_fifo_para_sistema(arquivo_origem, arquivo_destino)
    
    print("=" * 60)
    print("🎯 Pronto! Agora você pode importar o arquivo no sistema:")
    print(f"   📁 Arquivo: {arquivo_destino}")
    print("   🌐 Acesse: http://127.0.0.1:8000/importar-abastecimento/")
    print("   📤 Faça upload do arquivo gerado")

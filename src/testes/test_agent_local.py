import sys
import os

# Adiciona o diretório 'src' ao sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(base_dir, 'src'))

from agents.agente_verificador import AgenteVerificador

def test_agent():
    print("Iniciando teste do Agente Verificador...")
    try:
        agent = AgenteVerificador()
        test_cases = [
            "O limão congelado cura o câncer, segundo estudo de Harvard.",
            "O governo federal anunciou a abertura de novas vagas para o concurso do INSS."
        ]
        
        for case in test_cases:
            print(f"\n--- Testando: {case} ---")
            verdict = agent.verificar(case)
            print(f"Resultado: {verdict}")
            
    except Exception as e:
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_agent()

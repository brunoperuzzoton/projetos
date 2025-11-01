"""
YouTube Analyzer and Transcriber
Baixa, transcreve e analisa vídeos do YouTube

COMO USAR:
1. Instale as dependências: pip install pytube youtube-transcript-api
2. Execute o script: python "ia de ajuda.py"
3. Cole a URL do vídeo do YouTube
4. Escolha as opções do menu

COMPARTILHAMENTO:
- Envie este arquivo .py para qualquer pessoa
- A pessoa precisa ter Python instalado
- A pessoa precisa instalar as dependências (passo 1 acima)
"""

import sys
import re
from pathlib import Path

# Verifica e instala dependências automaticamente
def check_and_install_dependencies():
    """Verifica e oferece instalar dependências automaticamente"""
    required_packages = {
        'pytube': 'pytube',
        'youtube_transcript_api': 'youtube-transcript-api'
    }

    missing_packages = []

    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print("=" * 80)
        print("⚠️  DEPENDÊNCIAS FALTANDO")
        print("=" * 80)
        print(f"\nOs seguintes pacotes precisam ser instalados:")
        for pkg in missing_packages:
            print(f"  • {pkg}")

        print("\n" + "-" * 80)
        response = input("Deseja instalar automaticamente? (s/n): ").strip().lower()

        if response == 's':
            import subprocess
            print("\n📦 Instalando dependências...\n")
            for pkg in missing_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                    print(f"✅ {pkg} instalado com sucesso!")
                except Exception as e:
                    print(f"❌ Erro ao instalar {pkg}: {e}")

            print("\n✅ Instalação concluída! Reinicie o script.\n")
            sys.exit(0)
        else:
            print("\n❌ Instale manualmente com:")
            print(f"   pip install {' '.join(missing_packages)}\n")
            sys.exit(1)

# Verifica dependências antes de importar
check_and_install_dependencies()

# Agora importa as dependências
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


class YouTubeAnalyzer:
    """Classe para analisar e transcrever vídeos do YouTube"""

    def __init__(self, url):
        """
        Inicializa o analisador com a URL do YouTube

        Args:
            url (str): URL do vídeo do YouTube
        """
        self.url = url
        self.video_id = self._extract_video_id(url)
        self.yt = None
        self.transcript = None
        self.metadata = {}

    def _extract_video_id(self, url):
        """Extrai o ID do vídeo da URL do YouTube"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info(self):
        """Obtém informações do vídeo"""
        try:
            self.yt = YouTube(self.url)
            self.metadata = {
                'título': self.yt.title,
                'autor': self.yt.author,
                'duração': f"{self.yt.length // 60}:{self.yt.length % 60:02d}",
                'visualizações': self.yt.views,
                'descrição': self.yt.description[:200] + '...' if len(self.yt.description) > 200 else self.yt.description
            }
            return self.metadata
        except Exception as e:
            print(f"Erro ao obter informações do vídeo: {e}")
            return None

    def get_transcript(self, language='pt'):
        """
        Obtém a transcrição do vídeo usando legendas disponíveis

        Args:
            language (str): Código do idioma (padrão: 'pt' para português)

        Returns:
            str: Texto transcrito
        """
        if not self.video_id:
            print("ID do vídeo não encontrado")
            return None

        try:
            # Tenta obter legendas em português primeiro
            transcript_list = YouTubeTranscriptApi.get_transcript(self.video_id, languages=[language])
            self.transcript = ' '.join([entry['text'] for entry in transcript_list])
            return self.transcript
        except Exception as e:
            print(f"Erro ao obter legendas em {language}: {e}")

            # Tenta obter em inglês como fallback
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(self.video_id, languages=['en'])
                self.transcript = ' '.join([entry['text'] for entry in transcript_list])
                print("Legendas obtidas em inglês")
                return self.transcript
            except Exception as e2:
                print(f"Erro ao obter legendas: {e2}")
                return None

    def download_audio(self, output_path='downloads'):
        """
        Baixa o áudio do vídeo

        Args:
            output_path (str): Caminho para salvar o áudio

        Returns:
            str: Caminho do arquivo baixado
        """
        try:
            if not self.yt:
                self.yt = YouTube(self.url)

            # Cria o diretório se não existir
            Path(output_path).mkdir(parents=True, exist_ok=True)

            # Baixa apenas o áudio
            audio_stream = self.yt.streams.filter(only_audio=True).first()

            if audio_stream:
                print(f"Baixando áudio de: {self.yt.title}")
                output_file = audio_stream.download(output_path=output_path)
                print(f"Áudio salvo em: {output_file}")
                return output_file
            else:
                print("Nenhum stream de áudio disponível")
                return None

        except Exception as e:
            print(f"Erro ao baixar áudio: {e}")
            return None

    def analyze_content(self):
        """
        Analisa o conteúdo transcrito

        Returns:
            dict: Análise do conteúdo
        """
        if not self.transcript:
            print("Nenhuma transcrição disponível. Execute get_transcript() primeiro.")
            return None

        # Análise básica
        words = self.transcript.split()
        sentences = self.transcript.split('.')

        # Conta palavras mais frequentes
        word_freq = {}
        for word in words:
            word_clean = word.lower().strip('.,!?;:')
            if len(word_clean) > 3:  # Ignora palavras muito curtas
                word_freq[word_clean] = word_freq.get(word_clean, 0) + 1

        # Top 10 palavras mais frequentes
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        analysis = {
            'total_palavras': len(words),
            'total_sentenças': len([s for s in sentences if s.strip()]),
            'palavras_únicas': len(word_freq),
            'top_10_palavras': top_words,
            'duração_estimada_leitura': f"{len(words) / 200:.1f} minutos",  # ~200 palavras/min
            'resumo': self._generate_summary(sentences)
        }

        return analysis

    def _generate_summary(self, sentences, num_sentences=3):
        """Gera um resumo simples pegando as primeiras sentenças"""
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        summary_sentences = valid_sentences[:num_sentences]
        return '. '.join(summary_sentences) + '.'

    def save_transcript(self, filename='transcript.txt'):
        """
        Salva a transcrição em um arquivo

        Args:
            filename (str): Nome do arquivo para salvar
        """
        if not self.transcript:
            print("Nenhuma transcrição disponível")
            return False

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Transcrição do vídeo: {self.metadata.get('título', 'Desconhecido')}\n")
                f.write(f"Autor: {self.metadata.get('autor', 'Desconhecido')}\n")
                f.write(f"URL: {self.url}\n")
                f.write("=" * 80 + "\n\n")
                f.write(self.transcript)

            print(f"Transcrição salva em: {filename}")
            return True
        except Exception as e:
            print(f"Erro ao salvar transcrição: {e}")
            return False

    def generate_report(self):
        """Gera um relatório completo do vídeo"""
        print("\n" + "=" * 80)
        print("RELATÓRIO DE ANÁLISE DO VÍDEO DO YOUTUBE")
        print("=" * 80 + "\n")

        # Informações do vídeo
        if self.metadata:
            print("📹 INFORMAÇÕES DO VÍDEO:")
            for key, value in self.metadata.items():
                print(f"  • {key.capitalize()}: {value}")
            print()

        # Análise de conteúdo
        if self.transcript:
            analysis = self.analyze_content()
            if analysis:
                print("📊 ANÁLISE DE CONTEÚDO:")
                print(f"  • Total de palavras: {analysis['total_palavras']}")
                print(f"  • Total de sentenças: {analysis['total_sentenças']}")
                print(f"  • Palavras únicas: {analysis['palavras_únicas']}")
                print(f"  • Tempo estimado de leitura: {analysis['duração_estimada_leitura']}")
                print()

                print("🔑 TOP 10 PALAVRAS MAIS FREQUENTES:")
                for word, count in analysis['top_10_palavras']:
                    print(f"  • {word}: {count} vezes")
                print()

                print("📝 RESUMO:")
                print(f"  {analysis['resumo']}")
                print()

        print("=" * 80 + "\n")


def main():
    """Função principal para demonstração"""
    print("=" * 80)
    print("YOUTUBE ANALYZER & TRANSCRIBER")
    print("=" * 80)
    print()

    # Solicita URL do usuário
    url = input("Digite a URL do vídeo do YouTube: ").strip()

    if not url:
        print("URL inválida!")
        return

    # Cria o analisador
    analyzer = YouTubeAnalyzer(url)

    # Menu de opções
    while True:
        print("\n" + "-" * 80)
        print("OPÇÕES:")
        print("1. Obter informações do vídeo")
        print("2. Obter transcrição (legendas)")
        print("3. Baixar áudio")
        print("4. Analisar conteúdo")
        print("5. Gerar relatório completo")
        print("6. Salvar transcrição em arquivo")
        print("7. Nova URL")
        print("0. Sair")
        print("-" * 80)

        choice = input("\nEscolha uma opção: ").strip()

        if choice == '1':
            print("\n📹 Obtendo informações do vídeo...")
            info = analyzer.get_video_info()
            if info:
                for key, value in info.items():
                    print(f"  • {key.capitalize()}: {value}")

        elif choice == '2':
            print("\n📝 Obtendo transcrição...")
            language = input("Idioma (pt/en) [pt]: ").strip() or 'pt'
            transcript = analyzer.get_transcript(language)
            if transcript:
                print(f"\n✅ Transcrição obtida ({len(transcript)} caracteres)")
                show = input("Deseja ver a transcrição? (s/n): ").strip().lower()
                if show == 's':
                    print("\n" + "-" * 80)
                    print(transcript[:500] + "..." if len(transcript) > 500 else transcript)
                    print("-" * 80)

        elif choice == '3':
            print("\n🎵 Baixando áudio...")
            output_path = input("Pasta de destino [downloads]: ").strip() or 'downloads'
            audio_file = analyzer.download_audio(output_path)
            if audio_file:
                print(f"✅ Áudio baixado com sucesso!")

        elif choice == '4':
            print("\n📊 Analisando conteúdo...")
            analysis = analyzer.analyze_content()
            if analysis:
                print(f"\n  • Total de palavras: {analysis['total_palavras']}")
                print(f"  • Palavras únicas: {analysis['palavras_únicas']}")
                print(f"  • Top palavras: {', '.join([w[0] for w in analysis['top_10_palavras'][:5]])}")

        elif choice == '5':
            print("\n📋 Gerando relatório completo...")
            if not analyzer.metadata:
                analyzer.get_video_info()
            if not analyzer.transcript:
                analyzer.get_transcript()
            analyzer.generate_report()

        elif choice == '6':
            filename = input("Nome do arquivo [transcript.txt]: ").strip() or 'transcript.txt'
            analyzer.save_transcript(filename)

        elif choice == '7':
            url = input("\nDigite a nova URL do vídeo do YouTube: ").strip()
            if url:
                analyzer = YouTubeAnalyzer(url)
                print("✅ Nova URL carregada!")

        elif choice == '0':
            print("\n👋 Até logo!")
            break

        else:
            print("\n❌ Opção inválida!")


if __name__ == "__main__":
    main()

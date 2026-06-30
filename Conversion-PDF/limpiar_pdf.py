import argparse
import os
import re
from markitdown import MarkItDown

def remove_emojis(text):
    # Patrón Regex básico para emojis comunes
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # Emoticones
        "\U0001f300-\U0001f5ff"  # Símbolos y pictogramas
        "\U0001f680-\U0001f6ff"  # Transporte y mapas
        "\U0001f1e0-\U0001f1ff"  # Banderas
        "\U00002702-\U000027b0"  # Dingbats
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def clean_text(text):
    # 1. Quitar emojis
    text = remove_emojis(text)
    
    # 2. Quitar viñetas (asteriscos, guiones, signos más o viñetas redondas) al inicio de las líneas
    # Esto busca cualquier viñeta y los espacios que le siguen para borrarlos
    text = re.sub(r'^\s*[\*\-\+•]\s+', '', text, flags=re.MULTILINE)
    
    # 3. Limpiar espacios múltiples horizontales (tabs, varios espacios seguidos)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 4. Manejo de saltos de línea
    # Estandarizamos los saltos de línea (Windows a formato genérico)
    text = text.replace('\r\n', '\n')
    
    # A veces hay saltos de línea sencillos en medio de una oración (típico en PDFs).
    # Vamos a reemplazar 1 solo salto de línea por un espacio (para unir oraciones cortadas).
    # Pero si hay 2 o más saltos de línea juntos (separación de párrafos o títulos), los conservamos como 2.
    
    # Primero, si hay 3 o más saltos de línea, los reducimos a 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Reemplazamos 1 solo salto de línea (que no esté pegado a otro) por un espacio
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    
    # Quitamos espacios al principio y final del documento completo
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="Extrae texto de un PDF y lo limpia de impurezas.")
    parser.add_argument("archivo", help="Ruta del archivo PDF de entrada")
    parser.add_argument("-o", "--output", default=None, help="Nombre del archivo final (opcional). Si no se provee, usa 'nombre_original_limpio.md'")
    args = parser.parse_args()

    if args.output:
        archivo_salida = args.output
    else:
        # Obtenemos el directorio original y el nombre sin la extensión .pdf
        directorio = os.path.dirname(args.archivo)
        nombre_base = os.path.splitext(os.path.basename(args.archivo))[0]
        archivo_salida = os.path.join(directorio, f"{nombre_base}_limpio.md") if directorio else f"{nombre_base}_limpio.md"

    print(f"⏳ Extrayendo texto de '{args.archivo}'...")
    md = MarkItDown()
    
    try:
        # Convertir PDF a texto usando markitdown
        resultado = md.convert(args.archivo)
        texto_crudo = resultado.text_content
        
        print("🧹 Limpiando emojis, espacios innecesarios y viñetas...")
        texto_limpio = clean_text(texto_crudo)
        
        # Guardar en archivo
        with open(archivo_salida, "w", encoding="utf-8") as f:
            f.write(texto_limpio)
            
        print(f"✅ ¡Proceso completado! El archivo limpio se guardó como: {archivo_salida}")
        
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")

if __name__ == "__main__":
    main()

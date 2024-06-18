import struct

def read_bmp(file_path):
    try:
        with open(file_path, 'rb') as f:
            # Ler cabeçalho do BMP
            file_header = f.read(14)
            if file_header[:2] != b'BM':
                raise ValueError("Arquivo não é um BMP válido.")

            file_size = struct.unpack('<I', file_header[2:6])[0]
            print(f"Tamanho do arquivo: {file_size}")

            reserved1, reserved2 = struct.unpack('<HH', file_header[6:10])
            offset = struct.unpack('<I', file_header[10:14])[0]
            print(f"Offset para dados de pixel: {offset}")

            info_header = f.read(40)
            header_size = struct.unpack('<I', info_header[:4])[0]
            width = struct.unpack('<I', info_header[4:8])[0]
            height = struct.unpack('<I', info_header[8:12])[0]
            planes = struct.unpack('<H', info_header[12:14])[0]
            bpp = struct.unpack('<H', info_header[14:16])[0]

            print(f"Largura: {width}, Altura: {height}, Planos: {planes}, Bits por pixel: {bpp}")

            if planes != 1 or (bpp != 24 and bpp != 32):
                raise ValueError("O BMP não é de 24 ou 32 bits ou tem múltiplos planos.")

            pixels = []
            for y in range(height):
                row = []
                for x in range(width):
                    if bpp == 24:
                        pixel_data = f.read(3)
                        if len(pixel_data) != 3:
                            raise ValueError(f"Tamanho de pixel incorreto na posição ({x}, {y}). Esperado 3 bytes, mas obtido {len(pixel_data)} bytes.")
                        b, g, r = struct.unpack('BBB', pixel_data)
                    elif bpp == 32:
                        pixel_data = f.read(4)
                        if len(pixel_data) != 4:
                            raise ValueError(f"Tamanho de pixel incorreto na posição ({x}, {y}). Esperado 4 bytes, mas obtido {len(pixel_data)} bytes.")
                        b, g, r, a = struct.unpack('BBBB', pixel_data)
                    row.append((r, g, b))
                pixels.append(row)
                # Saltar padding de 4 bytes se necessário
                padding = (4 - (width * (bpp // 8) % 4)) % 4
                f.read(padding)
        return width, height, pixels
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        raise
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        raise

def write_bmp(file_path, width, height, pixels, bpp=24):
    try:
        with open(file_path, 'wb') as f:
            # Escreve cabeçalho BMP
            f.write(b'BM')
            size = 54 + width * height * (bpp // 8)
            f.write(struct.pack('<I', size))
            f.write(b'\x00\x00\x00\x00')
            f.write(b'\x36\x00\x00\x00')
            f.write(b'\x28\x00\x00\x00')
            f.write(struct.pack('<I', width))
            f.write(struct.pack('<I', height))
            f.write(b'\x01\x00')
            f.write(struct.pack('<H', bpp))
            f.write(b'\x00\x00\x00\x00')
            f.write(struct.pack('<I', width * height * (bpp // 8)))
            f.write(b'\x13\x0B\x00\x00')
            f.write(b'\x13\x0B\x00\x00')
            f.write(b'\x00\x00\x00\x00')
            f.write(b'\x00\x00\x00\x00')
            for row in pixels:
                for r, g, b in row:
                    f.write(struct.pack('BBB', b, g, r))
                # Adiciona padding se necessário
                padding = (4 - (width * (bpp // 8) % 4)) % 4
                f.write(b'\x00' * padding)
        print(f"Imagem salva em: {file_path}")
    except Exception as e:
        print(f"Erro ao escrever o arquivo {file_path}: {e}")
        raise

def rgb_to_grayscale(pixels):
    grayscale_pixels = []
    for row in pixels:
        grayscale_row = []
        for r, g, b in row:
            gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
            grayscale_row.append((gray, gray, gray))
        grayscale_pixels.append(grayscale_row)
    return grayscale_pixels

def binarize_image(pixels, threshold=128):
    binarized_pixels = []
    for row in pixels:
        binarized_row = []
        for r, g, b in row:
            gray = r  # since it's already grayscale
            binarized_pixel = 255 if gray > threshold else 0
            binarized_row.append((binarized_pixel, binarized_pixel, binarized_pixel))
        binarized_pixels.append(binarized_row)
    return binarized_pixels

def main(input_image_path, grayscale_output_path, binarized_output_path, threshold=128):
    try:
        print(f"Lendo imagem de entrada: {input_image_path}")
        width, height, pixels = read_bmp(input_image_path)

        print("Convertendo para níveis de cinza...")
        grayscale_pixels = rgb_to_grayscale(pixels)
        write_bmp(grayscale_output_path, width, height, grayscale_pixels)

        print("Binarizando a imagem...")
        binarized_pixels = binarize_image(grayscale_pixels, threshold)
        write_bmp(binarized_output_path, width, height, binarized_pixels)

        print("Processo concluído com sucesso.")
    except Exception as e:
        print(f"Erro no processo principal: {e}")

if __name__ == "__main__":
    input_image_path = "C:/Users/Jessica/Pictures/Saved Pictures/Bart.bmp"
    grayscale_output_path = "C:/Users/Jessica/Pictures/Saved Pictures/Bart_cinza.bmp"
    binarized_output_path = "C:/Users/Jessica/Pictures/Saved Pictures/Bart_binarizado.bmp"

    main(input_image_path, grayscale_output_path, binarized_output_path)


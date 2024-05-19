# -*- coding: utf-8 -*-
"""atividade3_processamento_imagens.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-g13lE4cco46PU9PL8BBdBnVr581K7BH
"""
# Bruna Correa Araujo Castro - 11819702 - SCC0251 - Atividade 3:Color & Segmentation & Morphology - 2024/1
import imageio.v3 as imageio
import numpy as np

def threshold(img, L):
    # cria uma matriz de zeros no mesmo tamanho da imagem
    new_img = np.zeros(img.shape)
    # onde os valores dos pixels são maiores que o limiar, o valor do pixel é redefinido para 1
    new_img[np.where(img >= L)] = 1
    return new_img

def otsu(img: np.ndarray, c = 0) -> np.ndarray:

  variancias = []

  # calcula o produto dos elementos de img.shape, ou seja, largura x altura = a quantidade de pixels total na matriz
  M = np.prod(img.shape)
  for i in np.arange(1,255):
    
    # histograma de quantidade de ocorrências de cada categoria de nivel grayscael
    hist_t,_ = np.histogram(img, bins=256, range=(0,256))

    # probabilidade da cor do pixel estar abaixo do threshold
    w_a = np.sum(hist_t[:i])/float(M)

    # probabilidade da cor do pixel estar acima do threshold
    w_b = np.sum(hist_t[i:])/float(M)

    # calculo da média de cada classe: multiplica a categoria pela quantidade de ocorrências dela, e divide pela soma de todas as ocorrências
    # mais um epsilon caso essa soma seja zero

    # classe "abaixo do threshold", vai até o threshold i hist[:i]
    media_abaixo = np.sum(np.arange(i) * hist_t[:i]) / (np.sum(hist_t[:i]) + 1e-6)

    # classe "acima do threshold", começa após o threshold i hist[i:]
    media_acima = np.sum(np.arange(i, 256) * hist_t[i:]) / (np.sum(hist_t[i:]) + 1e-6)

    # variancia interclasse
    var = w_a * w_b * (media_abaixo-media_acima)**2
    variancias.append(var)

  # computa a nova imagem, definindo como threshold a posição, ou seja, categoria que tem maior valor das variancias de toda a imagem
  new_img = threshold(img.copy(), np.argmax(variancias))

  return new_img


#Retorna a imagem erodita
def erosion(img, M, N):
    #Considere o Kernel = 3

    # kernel = np.array([[1,1,1],
    #                    [1,1,1],
    #                    [1,1,1]])
    new_img = img.copy()
    
    # itera pelas linhas, começando pela segunda e terminando na antepenultima
    for i in range(1,M-1):
        # itera pelas colunas, da mesma forma que nas linhas
        for j in range(1,N-1):
            # composição das linhas e colunas a serem avaliadas em uma iteração
            line_1 = img[i-1][j-1:j+2]
            line_2 = img[i][j-1:j+2]
            line_3 = img[i+1][j-1:j+2]
            iterado = np.array([line_1,line_2,line_3])
            # seta o pixel para o foreground apenas se ele corresponder completamente ao foreground
            # ou seja, pegando o mínimo valor da área analisada
            new_img[i][j] = np.min(iterado)

    return new_img
#Retorna a imagem dilatada
def dilation(img, M, N):

    #Considere o Kernel = 3
    # inicializa a nova imagem com base na antiga
    new_img = img.copy()
    
    # itera pelas linhas, começando pela segunda e terminando na antepenultima
    for i in range(1,M-1):
        # itera pelas colunas, da mesma forma que nas linhas
        for j in range(1,N-1):
            # composição das linhas e colunas a serem avaliadas em uma iteração
            # considera um kernel 3x3 

              line_1 = img[i-1][j-1:j+2]
              line_2 = img[i][j-1:j+2]
              line_3 = img[i+1][j-1:j+2]
              iterado = np.array([line_1,line_2,line_3])
              
              # seta o pixel para o foreground de qualquer parte corresponder a ele, ou seja, pega o máximo valor da área analisada
              new_img[i][j] = np.max(iterado)
    return new_img


def filter_gaussian(P, Q):
    s1 = P
    s2 = Q

    D = np.zeros([P, Q])  # Compute Distances
    for u in range(P):
        for v in range(Q):
            x = (u-(P/2))**2/(2*s1**2) + (v-(Q/2))**2/(2*s2**2)
            D[u, v] = np.exp(-x)
    return D

#Espectro Visível
# rosa, azul, verde, amarelo e vermelho
heatmap_colors = [
    [1, 0, 1],
    [0, 0, 1],
    [0, 1, 0],
    [1, 1, 0],
    [1, 0, 0]
]

# Function to map values to colors
def map_value_to_color(value, min_val, max_val, colormap):
    # Scale the value to the range [0, len(colormap) - 1]
    scaled_value = (value - min_val) / (max_val - min_val) * (len(colormap) - 1)
    # Determine the two closest colors in the colormap
    idx1 = int(scaled_value)
    idx2 = min(idx1 + 1, len(colormap) - 1)
    # Interpolate between the two colors based on the fractional part
    frac = scaled_value - idx1
    color = [
        (1 - frac) * colormap[idx1][0] + frac * colormap[idx2][0],
        (1 - frac) * colormap[idx1][1] + frac * colormap[idx2][1],
        (1 - frac) * colormap[idx1][2] + frac * colormap[idx2][2]
    ]
    return color

#Calcula o erro
def rms_error(img, out):
    M,N = img.shape
    error = ((1/(M*N))*np.sum((img-out)**2))**(1/2)
    return error




# lê a imagem de entrada a ser transformada
img = imageio.imread(input().rstrip())

#Transforma as imagem para escala de cinza

if len(img.shape) > 2: #Se for RGB converte para Gray, senão apenas mantém
  img = np.dot(img, [0.2989, 0.5870, 0.1140]).astype(np.int64)
  
#Transforma as imagem em binária
img_bin = otsu(img.copy(), c = 0)


# le a imagem de referencia
H  = imageio.imread(input().rstrip()) #Carrega a Imagem de Referencia

# le a lista de  entradas de indices de erosão ou dilatação, separa por espaço e transforma em inteiros
ciclo_morfologico = [int(x) for x in input().split()]

# Transforma as imagem com Operações Morfológicas
M,N = img.shape

for apply_morphology in ciclo_morfologico:
  if apply_morphology == 1:
    # Ciclo de Erosões (Expande a área de interesse PRETA e Reduz a BRANCA -> Voltar ao tamanho original sem ruído)
    img_bin = erosion(img_bin, M, N)
  elif apply_morphology == 2:
    # Ciclo de Dilatações (Expande a área de NÃO interesse BRANCA e Reduz a PRETA -> Redução de ruído)
    img_bin = dilation(img_bin, M, N)


# Transforma as imagens FINAIS

# Define alpha value for blending
alpha = 0.30  # Adjust this value to control the transparency of the heatmap


# Obtendo a máscara binária
mask = img_bin

#Coloração Gradiente
M, N = mask.shape[0], mask.shape[1]
color_distribution = filter_gaussian(M, N)
min_val = np.min(np.array(color_distribution))
max_val = np.max(np.array(color_distribution))

heatmap_image = np.zeros([M, N, 3]) #Imagem RGB vazia
for i in range(M):
    for j in range(N):
        heatmap_image[i, j] = map_value_to_color(color_distribution[i, j], min_val, max_val, heatmap_colors)

img_color = np.ones([M, N, 3]) #Imagem RGB vazia
indexes = np.where(mask==0)
img_color[indexes] = heatmap_image[indexes]

#Imagem final
gray_image = img
gray_image_normalized = gray_image / np.max(gray_image)


# coloca a imagem grayscale em cada um dos três canais rgb
c1 = gray_image_normalized*img_color[...,0]
c2 = gray_image_normalized*img_color[...,1]
c3 = gray_image_normalized*img_color[...,2]

# combina os canais em uma imagem RGB
gray_channels = np.stack((c1,c2,c3), axis=-1)

# Mix the grayscale image and heatmap using alpha compositing
mixed_image = gray_channels*(1-alpha) + alpha*img_color

#Calcula o erro para cada canal de cor
# Converte a escala da imagem referencia de 0 a 255 para 0 a 1 para comparar com a imagem mixada
error_R = rms_error(mixed_image[:,:,0], H[:,:,0]/255)
error_G = rms_error(mixed_image[:,:,1], H[:,:,1]/255)
error_B = rms_error(mixed_image[:,:,2], H[:,:,2]/255)
error = (error_R + error_G + error_B)/3
print(f"{error:.4f}")

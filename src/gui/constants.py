from src.core.constants import ALL_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS

MODEL_DESCRIPTIONS: dict[str, str] = {
    "u2netp": "Versao 'light' do u2net. Mais rapido, menos detalhe.",
    "u2net": "Modelo de uso geral, bom equilibrio entre velocidade e precisao.",
    "u2net_human_seg": "Alta precisao, especializado para recortar pessoas.",
    "isnet-general-use": "Moderno e porem pesado, mas com a melhor precisao para objetos.",
}

PRESET_COLORS: list[str] = [
    "#282a36",
    "#44475a",
    "#f8f8f2",
    "#6272a4",
    "#8be9fd",
    "#50fa7b",
    "#ffb86c",
    "#ff79c6",
    "#bd93f9",
    "#ff5555",
    "#f1fa8c",
]

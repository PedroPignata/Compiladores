"""Gera um vídeo curto a partir das capturas validadas da aplicação."""

from __future__ import annotations

from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = PROJECT_ROOT / "evidencias" / "capturas-de-tela"
OUTPUT = PROJECT_ROOT / "evidencias" / "video" / "demonstracao-transformer.mp4"
SIZE = (1280, 720)
FPS = 8
HOLD_FRAMES = 14
TRANSITION_FRAMES = 4

SCENES = (
    ("01-tela-inicial.png", "1. Entrada da frase e aviso educacional"),
    ("02-entrada-normalizacao.png", "2. Recebimento e normalização"),
    ("03-tokens-ids.png", "3. Tokens destacados e identificadores"),
    ("04-embeddings-posicao.png", "4. Embeddings didáticos e posição"),
    ("05-qkv-atencao.png", "5. Vetores Query, Key e Value"),
    ("05b-mapa-calor-atencao.png", "6. Pesos e mapa de calor da atenção"),
    ("06b-detalhe-camadas.png", "7. Duas cabeças e três camadas"),
    ("07-geracao-token-1.png", "8. Seleção do próximo token"),
    ("08-geracao-completa.png", "9. Geração progressiva concluída"),
    ("09-resultado-final.png", "10. Resposta e resumo final"),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def prepare_scene(filename: str, title: str) -> Image.Image:
    image = Image.open(SCREENSHOT_DIR / filename).convert("RGB").resize(SIZE)
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((32, 628, 1248, 696), radius=16, fill=(23, 32, 51, 225))
    draw.text((58, 646), title, font=font(26, bold=True), fill=(255, 255, 255, 255))
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    scenes = [prepare_scene(filename, title) for filename, title in SCENES]
    writer = imageio_ffmpeg.write_frames(
        str(OUTPUT),
        SIZE,
        fps=FPS,
        codec="libx264",
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        output_params=["-crf", "22", "-movflags", "+faststart"],
    )
    writer.send(None)
    try:
        previous: Image.Image | None = None
        for scene in scenes:
            if previous is not None:
                for step in range(1, TRANSITION_FRAMES + 1):
                    alpha = step / (TRANSITION_FRAMES + 1)
                    transition = Image.blend(previous, scene, alpha)
                    writer.send(np.asarray(transition, dtype=np.uint8))
            frame = np.asarray(scene, dtype=np.uint8)
            for _ in range(HOLD_FRAMES):
                writer.send(frame)
            previous = scene
    finally:
        writer.close()


if __name__ == "__main__":
    main()

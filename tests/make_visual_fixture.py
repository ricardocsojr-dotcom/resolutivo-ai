from pathlib import Path

from PIL import Image, ImageDraw

out = Path(__file__).resolve().parent / "fixtures" / "visual-law-fixture.png"
image = Image.new("RGB", (1000, 420), "white")
draw = ImageDraw.Draw(image)
draw.rectangle((40, 80, 260, 300), outline="#333333", width=3)
draw.rectangle((370, 80, 630, 300), outline="#333333", width=3)
draw.rectangle((740, 80, 960, 300), outline="#333333", width=3)
draw.line((260, 190, 370, 190), fill="#333333", width=4)
draw.line((630, 190, 740, 190), fill="#333333", width=4)
draw.text((92, 165), "Fato teste", fill="#222222")
draw.text((432, 165), "Análise teste", fill="#222222")
draw.text((802, 165), "Pedido teste", fill="#222222")
image.save(out)
print(out)

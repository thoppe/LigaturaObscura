import bs4, os, json, collections
from tqdm import tqdm
from source.fontHelper import Font

# Emoji Font source
# https://github.com/ellekasai/twemoji-awesome/blob/gh-pages/v1/twemoji-awesome.css

if __name__ == "__main__":
   
    f_source = 'data/ttx/roboto-v19-latin-regular.ttx'
    f_emoji = 'data/ttx/TwitterColorEmoji-SVGinOT.ttx'
    f_replace_tokens = "source/emoji_replace_tokens.json"
    
    #f_emoji = 'data/ttx/OpenSansEmoji.ttx'
    #f_emoji = 'data/ttx/SansBullshitSans.ttx'

    ligatures = { }
    glyph_additions = {
        'u1F386' : "fireworks",
    }

    #with open(f_replace_tokens) as FIN:
    #    glyph_additions = json.loads(FIN.read())

    # Simple check on the glyph additions (since it takes so long to load!)
    cx = collections.Counter(glyph_additions.values()).most_common(10)
    print(cx)
    
    if cx[0][1] > 1:
        raise ValueError("Repeated glyph")

    for val in glyph_additions.values():
        if len(val.split())>1:
            raise ValueError(f"Unsupported character (probably a space) in '{val}'")

    F0 = Font(f_source)
    F1 = Font(f_emoji)
    assert(F0.unitsPerEm == F1.unitsPerEm)

    for key, name in tqdm(glyph_additions.items()):
        g = F1.getGlyph(name=key)
        glyph_name = F0.add_glyph(g)

        ligatures[name] = glyph_name

    print("LIGATRUES", ligatures)

    F0.add_ligatures(ligatures)
    f_font = F0.save()
    F0.convert(f_font)

import bs4, os, json
from tqdm import tqdm
from source.fontHelper import Font

if __name__ == "__main__":
   
    f_source = 'data/ttx/roboto-v19-latin-regular.ttx'
    f_emoji = 'data/ttx/person.ttx'

    # These have to be done by hand for now
    glyph_additions = {
        "uniE900" : "pupper",
        "uniE901" : "Ramsey",
        "uniE902" : "Ariana",
    }

    F0 = Font(f_source)
    F1 = Font(f_emoji)

    print(F1.landmarks['GlyphOrder'])

    # Here we explictly force this out. In fact, use icomoons setting of 8192
    #assert(F0.unitsPerEm == F1.unitsPerEm)
    
    ligatures = { }
    for key, name in tqdm(glyph_additions.items()):
        g = F1.getGlyph(name=key)
        glyph_name = F0.add_glyph(g)
        ligatures[name] = glyph_name

    print("LIGATRUES", ligatures)
    
    F0.add_ligatures(ligatures)
    f_font = F0.save(suffix='_person')
    F0.convert(f_font)

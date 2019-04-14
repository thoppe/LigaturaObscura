import bs4, os, json
from tqdm import tqdm

f_gsub_template = 'source/gsub_template.xml'

class Font:

    def __init__(self, f_ttx):

        self.f_ttx = f_ttx

        print(f"Reading {f_ttx}")
        with open(self.f_ttx) as FIN:
            raw = FIN.read()
            
        self.soup = bs4.BeautifulSoup(raw, 'xml')

        # Editing gsub is stupid, let's just rip it out and put in our own
        with open(f_gsub_template) as FIN:
            gsub = bs4.BeautifulSoup(FIN.read(), 'xml')

        
        target = self.soup.find('GSUB')

        if target is None:
            self.soup.find('ttFont').append(gsub)
        else:
            target.replace_with(gsub)
        

        self.gsub = self.soup.find('GSUB')

        # Start at 600 and move up from here for each font
        self.unique_number_index = 600

        # Clear the hdmx table because it gave me problems
        hdmx = self.soup.find('hdmx')
        if hdmx is not None:
            hdmx.decompose()

        self.landmarks = {
            'GlyphOrder' : self.soup.find('GlyphOrder'),
            'hmtx' : self.soup.find('hmtx'),
            'glyf' : self.soup.find('glyf'),
        }


    def build_ligature_soup(self, target, glyph_out):
        ls = self.soup.new_tag('LigatureSet')

        first_letter, other_letters = target[0], target[1:]
        ls['glyph'] = first_letter

        other_letters = ','.join(other_letters)
        liga = self.soup.new_tag('Ligature')
        liga['glyph'] = glyph_out
        liga['components'] = other_letters
        ls.append(liga)
        return ls

    def add_ligatures(self, replacement_codes):
        
        gx = self.gsub.find('LigatureSubst')
        
        for key, val in replacement_codes.items():
            print(f"Replacing {key} with {val}")
            lig = self.build_ligature_soup(key, val)

            first_letter = key[0]

            # Look to see if we've already made a substitution
            has_replaced = False
            for ls in gx.find_all("LigatureSet"):
                if first_letter == ls["glyph"]:
                    ls.append(lig.find("Ligature"))
                    has_replaced = True
            if not has_replaced:
                gx.append(lig)

    def save(self, suffix=""):

        save_dest = 'data/parsed_ttx'
        os.system(f'mkdir -p {save_dest}')
        f_save = os.path.join(save_dest, os.path.basename(self.f_ttx))

        if suffix:
            f_save = f_save.split('.')
            f_save = '.'.join(f_save[:-1]) + suffix + '.'+ f_save[-1]
    
        soup = self.soup.ttFont

        with open(f_save, 'w') as FOUT:
            FOUT.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            FOUT.write(str(soup.prettify()))
            print(f"Saved to {f_save}")

        return f_save

    def convert(self, f_font):

        save_dest = 'docs/static/fonts'
        os.system(f'mkdir -p {save_dest}')

        f_save = os.path.join(save_dest, os.path.basename(f_font))
        f_save = '.'.join(f_save.split('.')[:-1]) + '.woff'

        cmd = f'ttx -f -o {f_save} {f_font}'
        os.system(cmd)
        print(f"Final save to {f_save}")

    @property
    def unitsPerEm(self):
        return int(self.soup.find("unitsPerEm")['value'])

    def getGlyph(self, glyphID=None, name=None):
        
        info = { }        

        if name is not None and glyphID is not None:
            raise ValueError("Must set only name or glyphID")

        if name is not None:
            tag = self.landmarks['GlyphOrder'].find('GlyphID', attrs={'name':name})
        
        if glyphID is not None:
            tag = self.landmarks['GlyphOrder'].find('GlyphID', attrs={'id':glyphID})


        if tag is None:
            print(f"CAN'T FIND {glyphID} {name}")
            return False    


        info['name'] = tag['name']

        attrs = {"name":info['name']}
        
        mtx = self.landmarks['hmtx'].find('mtx', attrs=attrs)
        info['lsb'] = int(mtx['lsb'])
        info['width'] = int(mtx['width'])
        
        info['TTGlyph'] = self.landmarks['glyf'].find('TTGlyph', attrs=attrs)
        return info

    

    
    def add_glyph(self, info, name=None):
        soup = self.soup

        # GlyphOrder/GlyphID in uniE600 range
        # <GlyphID id="211" name="uniE600"/>
        # Find the largest ID and increment one
        ID_LIST = [
            int(x['id']) for x in self.landmarks['GlyphOrder'].find_all("GlyphID")]
        next_id = max(ID_LIST) + 1

        if name is None:
            name = f"uniE{self.unique_number_index}"

        print("Adding glyph", name)
        
        attrs = {"id":next_id, "name":name,}

        self.unique_number_index += 1 # For each new glyph
        tag = soup.new_tag("GlyphID", attrs=attrs)
        self.landmarks["GlyphOrder"].append(tag)

        # hmtx/mtx
        #  <mtx name="uniE600" width="12218" lsb="79"/>
        attrs = {
            'width':info['width'],
            'lsb':info['lsb'],
            "name":name,
        }
        tag = soup.new_tag("mtx", attrs=attrs)
        self.landmarks['hmtx'].append(tag)

        # Add them to cmap all cmap_format_4 (may be multiple)
        # <map code="0xe600" name="uniE600"/><!-- ???? -->
        tag = soup.new_tag("map",
            attrs={'name':name,'code':f'0xe{next_id}'})
        for block in soup.find('cmap').find_all('cmap_format_4'):
            block.append(tag)

        # Add in the glyph info
        tag = info['TTGlyph']
        tag['name'] = name
        self.landmarks['glyf'].append(tag)
        
        self.unique_number_index += 1

        return name

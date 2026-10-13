import os, sys, re
import pdfplumber
import pandas as pd
from pathlib import Path

PDF_PATH = sys.argv[1]
OUT_EXCEL = sys.argv[2]

print(f'Reading PDF: {PDF_PATH}')

SYMBOLS = ['BOW AND ARROW', 'BOW AND', 'ARROW', 'LOTUS', 'HAND', 'CLOCK', 'BICYCLE', 'ELEPHANT',
           'KITE', 'BROOM', 'RAILWAY ENGINE', 'GAS CYLINDER', 'AUTO- RICKSHAW', 'AUTO-RICKSHAW',
           'AUTO-', 'RICKSHAW', 'CUP & SAUCER', 'CUP AND SAUCER', 'WHISTLE', 'BAT', 'TELEVISION',
           'GAS STOVE', 'COT', 'PRESSURE COOKER', 'ALMIRAH', 'HELICOPTER', 'CAMERA', 'RING',
           'BALLOON', 'KEY', 'ROAD ROLLER', 'BATSMAN', 'LAPTOP', 'FLUTE', 'FOOTBALL', 'CHALATA',
           'AIR CONDITIONER', 'BATTERY TORCH', 'BABY WALKER', 'BENCH', 'BINOCULARS', 'BLACK BOARD',
           'BREAD', 'BRIEF CASE', 'BRUSH', 'BUCKET', 'CAKE', 'CALCULATOR', 'CCTV CAMERA', 'CHAIN',
           'CHAKKI', 'CHESS BOARD', 'CHIMNEY', 'CLIP', 'COAT', 'DIAMOND', 'DISH ANTENNA', 'DOLL',
           'DRILL MACHINE', 'ELECTRIC POLE', 'ENVELOPE', 'FIBRE TRAY', 'FRYING PAN', 'FUNNEL',
           'GIFT PACK', 'GLASS TUMBLER', 'GRAMOPHONE', 'GRAPES', 'HARMONIUM', 'HAT', 'HEADPHONE',
           'HELMET', 'ICE CREAM', 'IMMERSION ROD', 'IRON', 'KETTLE', 'KITCHEN SINK', 'LADY PURSE',
           'LETTER BOX', 'LUNCH BOX', 'MIKE', 'MIXEE', 'NAIL CUTTER', 'NECK TIE', 'NOODLES BOWL',
           'PAN', 'PANT', 'PEANUTS', 'PEARS', 'PEN DRIVE', 'PENCIL SHARPENER', 'PENDULUM',
           'PINEAPPLE', 'PLASTER TROWEL', 'PLATE STAND', 'POT', 'PUNCHING MACHINE', 'RAZOR',
           'REFRIGERATOR', 'ROOM COOLER', 'ROOM HEATER', 'SAFETY PIN', 'SAW', 'SCISSORS',
           'SEWING MACHINE', 'SHIRT', 'SHOE', 'SINK', 'SKATES', 'SLATE', 'SOAP DISH', 'SOCKS',
           'STAMP', 'STAPLER', 'STETHOSCOPE', 'STOOL', 'SUITCASE', 'SWINGS', 'SYRINGE', 'TABLE',
           'TABLE LAMP', 'TEA STRAINER', 'TELEPHONE', 'TENT', 'TOOTH BRUSH', 'TOOTH PASTE',
           'TRACTOR CHALATA KISAN', 'TRUMPET', 'TYPEWRITER', 'TYRES', 'VACUUM CLEANER', 'VIOLIN',
           'WALKING STICK', 'WALL HANGING', 'WALLET', 'WATER CAN', 'WATER HEATER', 'WATER TANK',
           'WATER MELON', 'WINDOW', 'WINNOW', 'WOOL']

def clean_cand_name(name):
    name = re.sub(r'^\d+[\.\s]+', '', name).strip()
    name = re.sub(r'TURNOUT TOTAL.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'VALID VOTES.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Cup\s*&\s*Saucer', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Cup\s*&', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Bow\s*&\s*Arrow', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Bow\s*&', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Hockey\s*and\s*ball', '', name, flags=re.IGNORECASE)
    for s in SYMBOLS:
        name = re.sub(r'\b' + re.escape(s) + r'\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip(' -.,')
    return name

with pdfplumber.open(PDF_PATH) as pdf:
    full_text = '\n'.join(page.extract_text() or '' for page in pdf.pages)

pattern = r'(Constituency\s*[:\-.]?\s*(\d+)\s*\.?\s*([A-Za-z0-9\s\(\)\.\-]+?)\s+TOTAL ELECTORS\s*[:\-]?\s*([\d,]+))'
splits = list(re.finditer(pattern, full_text, flags=re.IGNORECASE))

rows = []

for idx, match in enumerate(splits):
    ac_no = int(match.group(2))
    raw_name = match.group(3).strip()
    electors = int(match.group(4).replace(',', ''))
    
    category = 'GEN'
    if '(SC)' in raw_name.upper() or '(S.C.)' in raw_name.upper():
        category = 'SC'
    elif '(ST)' in raw_name.upper() or '(S.T.)' in raw_name.upper():
        category = 'ST'
    
    start_pos = match.end()
    end_pos = splits[idx+1].start() if idx+1 < len(splits) else len(full_text)
    block_text = full_text[start_pos:end_pos]
    
    candidates = []
    lines = [l.strip() for l in block_text.split('\n') if l.strip()]
    
    blocks = []
    curr_block = []
    for line in lines:
        if 'TURN OUT TOTAL:' in line.upper() or 'VALID VOTES' in line.upper() or 'CANDIDATE NAME' in line.upper() or line.upper().startswith('PAGE '):
            continue
        if re.match(r'^\d+\s+[A-Za-z]', line) or re.match(r'^\d+\s+NOTA', line):
            if curr_block: blocks.append(curr_block)
            curr_block = [line]
        elif line.strip() != '0':
            curr_block.append(line)
    if curr_block: blocks.append(curr_block)

    for cand_idx, block in enumerate(blocks):
        block_text_cand = ' '.join(block)
        
        vm = re.search(r'\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d\.]+)\s*', block_text_cand)
        if not vm:
            continue
            
        evm = int(vm.group(1).replace(',', ''))
        postal = int(vm.group(2).replace(',', ''))
        total = int(vm.group(3).replace(',', ''))
        pct = float(vm.group(4))
        
        meta_part = block_text_cand[:vm.start()].strip()
        end_part = block_text_cand[vm.end():].strip()
        
        if 'NOTA' in meta_part.upper():
            rows.append({
                'STATE/UT NAME': 'Maharashtra',
                'AC NO.': ac_no,
                'AC NAME': raw_name,
                'CANDIDATE NAME': str(cand_idx + 1) + ' NOTA',
                'GENDER': None,
                'AGE': None,
                'CATEGORY': category,
                'PARTY': 'NOTA',
                'SYMBOL': 'NOTA',
                'GENERAL': evm,
                'POSTAL': postal,
                'TOTAL': total,
                'OVER VALID VOTES + NOTA': pct,
                'OVER TOTAL ELECTORS': round((total/electors)*100, 2) if electors else 0.0,
                'TOTAL ELECTORS': electors
            })
            continue
            
        gm = re.search(r'(MALE|FEMALE|THIRD GENDER|M|F|O)\s+(\d+)\s+(GENERAL|GEN|SC|ST)\s+([A-Za-z0-9\(\)\-]+)', meta_part, re.IGNORECASE)
        if gm:
            gender = 'M' if 'M' in gm.group(1).upper() else ('F' if 'F' in gm.group(1).upper() else 'O')
            age = int(gm.group(2))
            raw_party = gm.group(4).upper()
            
            cand_name_start = meta_part[:gm.start()].strip()
            cand_name_end = meta_part[gm.end():].strip()
            
            raw_full = f"{cand_name_start} {cand_name_end} {end_part}".strip()
            clean_full = clean_cand_name(raw_full)
            if not clean_full: clean_full = f"Candidate {cand_idx + 1}"
            
            rows.append({
                'STATE/UT NAME': 'Maharashtra',
                'AC NO.': ac_no,
                'AC NAME': raw_name,
                'CANDIDATE NAME': str(cand_idx + 1) + ' ' + clean_full,
                'GENDER': 'MALE' if gender == 'M' else ('FEMALE' if gender == 'F' else 'OTHER'),
                'AGE': age,
                'CATEGORY': category,
                'PARTY': raw_party,
                'SYMBOL': '', # Not strictly parsing symbols out cleanly right now
                'GENERAL': evm,
                'POSTAL': postal,
                'TOTAL': total,
                'OVER VALID VOTES + NOTA': pct,
                'OVER TOTAL ELECTORS': round((total/electors)*100, 2) if electors else 0.0,
                'TOTAL ELECTORS': electors
            })

df = pd.DataFrame(rows)

# To perfectly mimic the header structure (Row 1 empty, Row 2 title, Row 3 headers)
writer = pd.ExcelWriter(OUT_EXCEL, engine='xlsxwriter')
df.to_excel(writer, sheet_name='Worksheet', startrow=2, index=False)
workbook = writer.book
worksheet = writer.sheets['Worksheet']
worksheet.write('A2', '10 - Detailed Results')
writer.close()

print(f'Exported to Excel: {OUT_EXCEL} with {len(df)} rows.')

"""Compact public catalog; generated from extracted game data and editor's curated image list."""
import json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'STARDIVE_Extract'/'data'
EDITOR=ROOT.parent/'MonGilPartyManagers-main'
def read(name):return json.loads((SOURCE/(name+'.json')).read_text(encoding='utf-8-sig'))
monsters=json.loads((ROOT/'source-monsters.json').read_text(encoding='utf-8'))
breeds={b['name']:b for b in read('monsterling_breeds')}
cards={c['item_id']:c for c in read('monsterling_all_grades_stats_1_60')}
chains=read('link_chain_levels')
recipe=json.loads((ROOT/'recipes/data.js').read_text(encoding='utf-8').split('window.MONGIL_RECIPES = ',1)[1].rstrip().rstrip(';'))
recipe_ids={m['id'] for m in recipe['monsters']}
local=next(x['Rows'] for x in json.loads((SOURCE.parent/'tables_json/LOCAL.json').read_text(encoding='utf-8-sig')) if 'Rows'in x)
plain=lambda s:re.sub(r'<[^>]*>','',s).replace('\\n','\n').strip()
labels={i:plain(local['COLOR_ELEMENT_TYPE_NAME_'+str(i)]['TEXT']).replace(' 속성 피해','') for i in range(1,9)}
main=['땅','바람','번개','불','얼음']
def categories(text):
    # Remove the activation clause; preserve enemy-element restrictions in unconditional effects.
    effect=re.split(r'(?:성공|적중|공격|피격|사용|처치) 시|성공 시|\d+회 피격 시',text,maxsplit=1)[-1]
    names=[n for n in labels.values() if re.search(re.escape(n)+r'\s*속성',effect)]
    return names or ['공용']
result=[]
for m in monsters:
    b=breeds[m['name']];effects=[]
    for grade in range(1,6):
        c=cards[b['items_by_grade'][str(grade)]];desc=c['effect']['description']
        assert not desc['unresolved_placeholders']
        effects.append(desc['text'])
    levels=[]
    for c in sorted((c for c in chains if c['monster_id']==b['monster_id']),key=lambda c:c['upgrade_level']):
        element=labels[c['skill']['ELEMENTAL_TYPE']]
        text=c['description_text'].replace('{1}',element+' 속성 피해').replace('{3}','')
        text=re.sub(r'^.*?몬스터링 장착 시 등장 조건에 따라 나타나\s*','',text,count=1)
        text=re.sub(r'\n{3,}','\n\n',text).strip()
        assert not re.search(r'\{\d+\}',text)
        extra=text.split('[추가 효과]',1)[1].strip() if '[추가 효과]' in text else ''
        granted=[line.strip() for line in extra.splitlines() if line.strip()]
        intro=text.split('[등장 조건]',1)[0]
        for phrase,label in [('적을 공중에 띄','적을 공중에 띄웁니다.'),('끌어당','주변의 적을 끌어당깁니다.')]:
            if phrase in intro and not any(label in x for x in granted):granted.append(label)
        effect_categories=list(dict.fromkeys(cat for line in granted for cat in categories(line))) if granted else ['효과 없음']
        levels.append({'effects':granted,'categories':effect_categories,'level':c['upgrade_level'],'element':element,'cooldown':c['cooldown_seconds'],'damage':c['damage_percent'],'condition':c['condition_text'],'text':text})
    result.append({'id':str(b['monster_id']),'name':m['name'],'image':m['image'],'recipe':str(b['monster_id']) in recipe_ids,'categories':categories(effects[0]),'effects':effects,'cooldown':float(re.search(r'([\d.]+)초에 1회',effects[0])[1]) if re.search(r'([\d.]+)초에 1회',effects[0]) else None,'chains':levels})
assert len(result)==196 and len({r['id'] for r in result})==196
recipe_effects=[{k:r[k] for k in ['id','name','effects','cooldown','categories']}|{'chains':[{k:c[k] for k in ['level','effects','condition','cooldown','categories']} for c in r['chains']]} for r in result if r['id'] in recipe_ids]
assert len(recipe_effects)==len(recipe_ids)
(ROOT/'recipes/effects-data.js').write_text('/* Selected-monster summaries; loaded only after selection. */\nwindow.MONLING_RECIPE_EFFECTS='+json.dumps(recipe_effects,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
(ROOT/'catalog-data.js').write_text('/* Generated; no raw tables at runtime. */\nwindow.MONLING_CATALOG='+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
# Copy only images referenced by this catalog or recipes. Each repository can deploy independently.
recipe=json.loads((ROOT/'recipes/data.js').read_text(encoding='utf-8').split('window.MONGIL_RECIPES = ',1)[1].rstrip().rstrip(';'))
images={r['image'] for r in result}|{r['image'] for r in recipe['monsters']}
for image in images:
    src=EDITOR/image;dest=ROOT/image
    assert src.is_file(),src
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
print('Built',len(result),'monsters;',len(images),'images;', (ROOT/'catalog-data.js').stat().st_size,'data bytes')

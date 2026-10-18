const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),c={window:{}};vm.createContext(c);
for(const f of ['recipes/data.js','recipes/engine.js'])vm.runInContext(fs.readFileSync(path.join(root,f),'utf8'),c);
const data=c.window.MONGIL_RECIPES,g=c.window.MongilRecipeEngine.create(data),get=name=>g.search(name).find(m=>m.name===name);
assert.equal(data.recipes.length,76);assert.equal(data.monsters.length,168);
for(const m of data.monsters){assert.ok(fs.existsSync(path.join(root,m.image)));assert.ok(!m.name.includes('MONSTER_NAME_'));g.tree(m.id);g.leaves(m.id);}
const blue=get('청영'),stone=get('석괴호'),ghost=get('천시원령');assert.ok(blue&&stone&&ghost);
const blueTree=g.tree(blue.id);assert.ok(blueTree.children.some(x=>x.monster.id===stone.id));
const leafNames=g.leaves(blue.id).map(x=>x.name).sort();assert.equal(JSON.stringify(leafNames),JSON.stringify(['적영','설귀호','천시령','질풍령'].sort()));
assert.equal(g.leaves(blue.id).reduce((s,x)=>s+x.count,0),4);
assert.ok(g.ancestors(stone.id).some(x=>x.id===blue.id));assert.ok(g.roots(ghost.id).some(x=>x.id===blue.id));
assert.ok(g.tree(stone.id).children.some(x=>x.monster.id===ghost.id));
assert.equal(g.search(' 청 영 ')[0].id,blue.id);assert.equal(g.search('nonexistent').length,0);
assert.ok(g.search('콜로서스얼터').some(x=>x.name==='콜로서스 얼터'));assert.ok(data.recipes.every(x=>x.successRate===100));
// Repeated basic ingredients count twice; cyclic input cannot recurse indefinitely.
const fixture={monsters:[{id:'a',name:'A'},{id:'b',name:'B'}],recipes:[{id:'r',ingredients:['a','a'],result:'b'}]};assert.equal(c.window.MongilRecipeEngine.create(fixture).leaves('b')[0].count,2);
assert.throws(()=>c.window.MongilRecipeEngine.create({...fixture,recipes:[{ingredients:['b','a'],result:'b'}]}).tree('b'),/순환/);
console.log('PASS: moved recipes preserve all 76 formulas, 168 icons, full and reverse trees, search and cycle rejection');

const effectsContext={window:{}};vm.createContext(effectsContext);vm.runInContext(fs.readFileSync(path.join(root,'recipes/effects-data.js'),'utf8'),effectsContext);const effects=effectsContext.window.MONLING_RECIPE_EFFECTS;assert.equal(effects.length,data.monsters.length);for(const monster of data.monsters){const row=effects.find(r=>r.id===monster.id);assert.ok(row);assert.equal(row.effects.length,5);for(const chain of row.chains)assert.ok(Array.isArray(chain.effects)&&Number.isFinite(chain.cooldown));}assert.ok(!fs.readFileSync(path.join(root,'recipes/index.html'),'utf8').includes('effects-data.js'),'summary data stays lazy');console.log('PASS: all 168 recipe monsters have 5-grade effect summaries; summary data loaded only on selection');

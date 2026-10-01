from pathlib import Path
import hashlib, importlib.util, json, sys, xml.etree.ElementTree as ET
ROOT=Path('/workspace/MVP-PPG')
WORK=Path('/workspace/ppg-rs422-no-tvs-work')
REMOVED={'D2','D4'}
def load_design(path, name):
    sp=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
old_design=load_design(WORK/'before/kicad/design_v08.py','old_design')
new_design=load_design(ROOT/'kicad/design_v08.py','new_design')
assert set(old_design.COMPONENTS)-set(new_design.COMPONENTS)==REMOVED
assert len(new_design.COMPONENTS)==37
assert all(old_design.COMPONENTS[r]==c for r,c in new_design.COMPONENTS.items()), 'Surviving model metadata changed'
def xml_model(path):
    root=ET.parse(path).getroot()
    comps={c.attrib['ref']:ET.tostring(c,encoding='unicode') for c in root.findall('./components/comp')}
    nets={n.attrib['name']:{(p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')} for n in root.findall('./nets/net')}
    return comps,nets
old_comps,old_nets=xml_model(ROOT/'docs/verification_rs422_schematic/netlist.xml')
new_comps,new_nets=xml_model(WORK/'validation/netlist.xml')
assert set(old_comps)-set(new_comps)==REMOVED and len(new_comps)==37
assert all(old_comps[r]==c for r,c in new_comps.items()), 'Surviving component XML changed'
expected_nets={n:{p for p in nodes if p[0] not in REMOVED} for n,nodes in old_nets.items()}
expected_nets={n:v for n,v in expected_nets.items() if v}
assert expected_nets==new_nets, 'Net nodes differ beyond D2/D4 removal'
actual_pin_net={p:n.lstrip('/') for n,nodes in new_nets.items() for p in nodes}
for ref,c in new_design.COMPONENTS.items():
    for pin,net in c['pins'].items():
        actual=actual_pin_net.get((ref,pin))
        if net is None:
            assert actual and actual.startswith('unconnected-'), (ref,pin,actual)
        else:
            assert actual==net,(ref,pin,net,actual)
sys.path.insert(0,str(ROOT/'kicad'))
import layout_schematic_v08 as L
def uuids(path):
    root=L.parse(path.read_text()); result={}
    for s in L.children(root,'symbol'):
        ref=str(L.prop(s,'Reference')[2])
        if ref.startswith('#'): continue
        result[ref]={'symbol':str(L.get(s,'uuid')[1]),'pins':{str(p[1]):str(L.get(p,'uuid')[1]) for p in L.children(s,'pin')}}
    return str(L.get(root,'uuid')[1]),result
old_root,old_ids=uuids(WORK/'before/kicad/ppg_pcb_v08.kicad_sch')
new_root,new_ids=uuids(ROOT/'kicad/ppg_pcb_v08.kicad_sch')
assert old_root==new_root
assert set(old_ids)-set(new_ids)==REMOVED and len(new_ids)==37
assert all(old_ids[r]==v for r,v in new_ids.items()), 'Surviving component/pin UUID changed'
erc=json.loads((WORK/'validation/erc.json').read_text())
violations=[v for s in erc['sheets'] for v in s.get('violations',[])]
assert not violations
files=['design_v08.py','build_sch_v08.py','layout_schematic_v08.py','SleepBud.kicad_sym','ppg_pcb_v08.kicad_sch']
report={'status':'pass','components_before':len(old_comps),'components_after':len(new_comps),'removed_references':sorted(REMOVED),'removed_net_nodes':sorted([list(p) for nodes in old_nets.values() for p in nodes if p[0] in REMOVED]),'remaining_model_dicts_exactly_unchanged':True,'remaining_component_xml_exactly_unchanged':True,'nets_equal_baseline_minus_removed_nodes':True,'model_netlist_pin_parity':True,'remaining_component_and_pin_uuids_preserved':True,'root_schematic_uuid_preserved':True,'erc_violations':len(violations),'net_count':len(new_nets),'sha256':{f:hashlib.sha256((ROOT/'kicad'/f).read_bytes()).hexdigest() for f in files}}
(WORK/'validation/invariant_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

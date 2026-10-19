"""Generate only the separate PPG UART adapter schematic and local libraries."""
from pathlib import Path
import json, uuid, hashlib, shutil, csv, re

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
NAME='ppg_uart_adapter_v01'
NS=uuid.UUID('2f222e06-dc81-441f-8139-e0593a63d64e')
uid=lambda s:str(uuid.uuid5(NS,s))
ROOT=uid('root')
q=lambda s:json.dumps(str(s),ensure_ascii=False)
def fx(size=1.27,hide=False,justify=''):
 return f'(effects (font (face "Malgun Gothic") (size {size} {size}))'+(' (hide yes)' if hide else '')+(f' (justify {justify})' if justify else '')+')'
def prop(n,v,x=0,y=0,hide=False,size=1.27):
 return f'(property {q(n)} {q(v)} (at {x} {y} 0) {fx(size,hide,"left")})'
def pin(n,nm,typ,x,y,a,length=5.08):
 return f'(pin {typ} line (at {x} {y} {a}) (length {length}) (name {q(nm)} {fx(1.016)}) (number {q(n)} {fx(1.016)}))'
def rect(x1,y1,x2,y2):
 return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width .254) (type default)) (fill (type background)))'
def line(points,width=.254):
 return '(polyline (pts '+' '.join(f'(xy {x} {y})' for x,y in points)+f') (stroke (width {width}) (type default)) (fill (type none)))'
LIB={};PINS={};items=[];COMP={};counter=0
def symbol(name,ref,body,pins,power=False):
 PINS[name]=pins
 props=' '.join(prop(n,v,hide=n not in ['Reference','Value']) for n,v in [('Reference',ref),('Value',name),('Footprint',''),('Datasheet',''),('Description',name)])
 LIB[name]=f'(symbol "Adapter:{name}" '+('(power) ' if power else '')+f'(pin_names (offset .762)) (exclude_from_sim no) (in_bom {"no" if power else "yes"}) (on_board yes) {props} (symbol "{name}_0_1" {body}) (symbol "{name}_1_1" '+ ' '.join(pin(*p) for p in pins)+'))'

symbol('LD1117_3V3','U',rect(-10.16,-7.62,10.16,7.62),[
 ('3','VIN','power_in',-15.24,2.54,0),('2','VOUT / TAB','power_out',15.24,2.54,180),('1','GND','power_in',0,-12.7,90)])
symbol('XR33183','U',rect(-10.16,-12.7,10.16,12.7),[
 ('6','A (+)','input',-15.24,5.08,0),('4','B (-)','input',-15.24,-5.08,0),('3','RO','output',15.24,0,180),
 ('1','VCC','power_in',0,17.78,270),('2','GND','power_in',0,-17.78,90),('5','~{EN}','input',-15.24,-10.16,0)])
symbol('XR33194','U',rect(-10.16,-12.7,10.16,12.7),[
 ('1','DI','input',-15.24,0,0),('6','Y (+)','output',15.24,5.08,180),('4','Z (-)','output',15.24,-5.08,180),
 ('2','VCC','power_in',0,17.78,270),('5','GND','power_in',0,-17.78,90),('3','DE','input',-15.24,10.16,0)])
symbol('R_V','R',rect(-1.016,-2.54,1.016,2.54),[('1','','passive',0,3.81,270,1.27),('2','','passive',0,-3.81,90,1.27)])
symbol('R_H','R',rect(-2.54,-1.016,2.54,1.016),[('1','','passive',-3.81,0,0,1.27),('2','','passive',3.81,0,180,1.27)])
capbody=line([(-2.032,.762),(2.032,.762)],.508)+line([(-2.032,-.762),(2.032,-.762)],.508)
symbol('C','C',capbody,[('1','','passive',0,3.81,270,2.794),('2','','passive',0,-3.81,90,2.794)])
symbol('FerriteBead','FB',line([(-1.8,-1),(1.1,1.8),(1.8,1),(-1.1,-1.8),(-1.8,-1)]),[('1','','passive',-3.81,0,0,2.54),('2','','passive',3.81,0,180,2.54)])
symbol('SM712','D',rect(-7.62,-7.62,7.62,7.62),[('1','IO1','passive',-12.7,5.08,0),('2','IO2','passive',-12.7,-5.08,0),('3','GND','passive',0,-12.7,90)])
tvsbody=line([(-1.27,.762),(1.27,.762),(1.27,1.27)])+line([(-1.27,-1.27),(1.27,-1.27),(0,.762),(-1.27,-1.27)])
symbol('TVS_Uni','D',tvsbody,[('1','','passive',0,3.81,270,2.54),('2','','passive',0,-3.81,90,2.54)])
for n in [2,4,6]:
 offsets=[((n-1)/2-i)*5.08 for i in range(n)]
 symbol('Port'+str(n),'J',rect(-7.62,min(offsets)-2.54,7.62,max(offsets)+2.54),[(str(i+1),'','passive',12.7,v,180,5.08) for i,v in enumerate(offsets)])
symbol('PWR_FLAG','#FLG',line([(0,0),(0,1.27),(-1.27,1.905),(0,2.54),(1.27,1.905),(0,1.27)]),[('1','','power_out',0,0,90,0)],True)
# Mechanical fabrication item: no electrical pins and no copper connection.
symbol('MountingHole_3mm','H',
 '(circle (center 0 0) (radius 2.54) (stroke (width .254) (type default)) (fill (type none)))'
 '(circle (center 0 0) (radius .762) (stroke (width .127) (type default)) (fill (type none)))',[])


def add(s):
 global counter
 counter+=1
 items.append(s.replace('@UUID@',uid('item'+str(counter))))
def wire(a,b):
 if a==b:return
 add(f'(wire (pts (xy {a[0]:.4f} {a[1]:.4f}) (xy {b[0]:.4f} {b[1]:.4f})) (stroke (width 0) (type default)) (uuid "@UUID@"))')
def junction(x,y):add(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "@UUID@"))')
def label(n,x,y,right=False):add(f'(label {q(n)} (at {x:.4f} {y:.4f} 0) {fx(1.27,False,"right bottom" if right else "left bottom")} (uuid "@UUID@"))')
def text(s,x,y,size=1.524):add(f'(text {q(s)} (exclude_from_sim no) (at {x} {y} 0) {fx(size,False,"left top")} (uuid "@UUID@"))')
def normalized_fields(ref,value,mpn=''):
 """Consistent display values; ratings stay in hidden fields/BOM columns."""
 voltage=tolerance=dielectric=''
 if re.fullmatch(r'R\d+',ref):
  match=re.fullmatch(r'(\d+(?:\.\d+)?)\s*(k|kΩ|Ω|ohm)?(?:\s*/\s*(\d+(?:\.\d+)?%))?',value)
  if not match:raise ValueError((ref,value))
  number,unit,tolerance=match.groups();tolerance=tolerance or ''
  value=number+' '+('kΩ' if unit in ('k','kΩ') else 'Ω')
 elif re.fullmatch(r'C\d+',ref):
  match=re.fullmatch(r'(\d+(?:\.\d+)?)\s*(nF|uF|µF)(?:\s*/?\s*(\d+(?:\.\d+)?)\s*V)?(?:\s+(X[56789][RSP]))?',value)
  if not match:raise ValueError((ref,value))
  number,unit,voltage,dielectric=match.groups()
  value=number+' '+unit.replace('uF','µF');voltage=(voltage+' V') if voltage else '';dielectric=dielectric or ''
  if mpn=='C1608X5R1A226M080AC':tolerance='20%';dielectric='X5R'
 elif mpn and re.fullmatch(r'(U|D|FB)\d+',ref):value=mpn
 return value,{'Voltage':voltage,'Tolerance':tolerance,'Dielectric':dielectric}

def place(ref,sym,x,y,value,footprint,nets,mpn='',maker='',ds='',desc='',props=None):
 value,ratings=normalized_fields(ref,value,mpn)
 assert set(nets)=={p[0] for p in PINS[sym]},ref
 COMP[ref]={'symbol':sym,'value':value,'footprint':footprint,'nets':nets,'mpn':mpn,'manufacturer':maker,'datasheet':ds,'description':desc,'at':[x,y]}
 COMP[ref].update({key.lower():value for key,value in ratings.items()})
 if props is None:props=(x+3.81,y-1.905,x+3.81,y+1.905)
 p=prop('Reference',ref,props[0],props[1],ref.startswith('#'))+prop('Value',value,props[2],props[3])
 for n,v in [('Footprint',footprint),('Datasheet',ds),('Description',desc),('MPN',mpn),('Manufacturer',maker)]:p+=prop(n,v,x,y,True)
 for n,v in ratings.items():
  if v:p+=prop(n,v,x,y,True)
 power=ref.startswith('#')
 items.append(f'(symbol (lib_id "Adapter:{sym}") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom {"no" if power else "yes"}) (on_board yes) (dnp no) (uuid "{uid(ref)}") {p} '+ ' '.join(f'(pin "{n}" (uuid "{uid(ref+"."+n)}"))' for n in nets)+f' (instances (project "{NAME}" (path "/{ROOT}" (reference "{ref}") (unit 1)))))')
 return {p[0]:(round(x+p[3],4),round(y-p[4],4)) for p in PINS[sym]}
def stub(p,n,d='R',length=5.08):
 ends={'R':(p[0]+length,p[1]),'L':(p[0]-length,p[1]),'U':(p[0],p[1]-length),'D':(p[0],p[1]+length)}
 e=ends[d];wire(p,e);label(n,*e,right=d=='L')
def cap(ref,x,y,val,fp,net,polar=False,**kw):
 p=place(ref,'C_Polarized' if polar else 'C',x,y,val,fp,{'1':net,'2':'GND'},**kw)
 stub(p['1'],net,'U',2.54);stub(p['2'],'GND','D',2.54)
 return p
def shunt(ref,x,y,net):
 p=place(ref,'TVS_Uni',x,y,'ESD351DPYR','Adapter:TI_DPY0002A_1x0.6',{'1':net,'2':'GND'},'ESD351DPYR','Texas Instruments','https://www.ti.com/lit/ds/symlink/esd351.pdf','UART connector ESD shunt; route pad to TVS landing before internal series resistor')
 stub(p['1'],net,'U',2.54);stub(p['2'],'GND','D',2.54)
def resistor(ref,x,y,val,n1,n2,vertical=False,footprint='Resistor_SMD:R_0603_1608Metric',**kw):
 return place(ref,'R_V' if vertical else 'R_H',x,y,val,footprint,{'1':n1,'2':n2},props=(x+2.54,y-1.27,x+2.54,y+2.54) if vertical else (x-3.81,y-5.08,x-3.81,y-2.54),**kw)
def port(ref,n,x,y,value,nets):
 p=place(ref,'Port'+str(n),x,y,value,f'Adapter:WirePads_1x{n:02d}_P1.8mm_D1.2',nets,desc='Wire solder pads; connector mechanical implementation to be reviewed with PCB outline',props=(x-7.62,y-n*2.54-6.35,x-7.62,y-n*2.54-2.54))
 for num,net in nets.items():stub(p[num],net)

text('PPG 연결 보드 / 6-wire RS-422 to 4-pin 3.3V UART',12.7,13.97,2.54)
text('공통 9V 입력 · LD1117-3.3V · R1~R8·MLCC 1608 / R9 3216 / 탄탈 없음 · 동일 6층 0.8mm 패널 제작 예정',12.7,20.32)
text('01  전원 / 9V shared supply',12.7,29.21,1.905)
port('J1',2,25.4,50.8,'9V INPUT',{'1':'9V_SHARED','2':'GND'})
fb=place('FB1','FerriteBead',76.2,48.26,'BLM15PX601SN1D','Inductor_SMD:L_0402_1005Metric',{'1':'9V_SHARED','2':'9V_LDO'},'BLM15PX601SN1D','Murata','https://www.murata.com/en-us/products/productdetail?partno=BLM15PX601SN1%23','Local LDO input filter; PPG power branches before this bead',props=(66.04,39.37,66.04,43.18))
stub(fb['1'],'9V_SHARED','L',7.62)
u=place('U1','LD1117_3V3',114.3,50.8,'LD1117S33TR','Package_TO_SOT_SMD:SOT-223-3_TabPin2',{'1':'GND','2':'3V3','3':'9V_LDO'},'LD1117S33TR','STMicroelectronics','https://www.st.com/resource/en/datasheet/ld1117.pdf','User-selected fixed 3.3V LDO; pins1 GND,2 OUT,3 IN; tab electrically OUT',props=(104.14,36.83,104.14,40.64))
wire(fb['2'],u['3']);label('9V_LDO',85.09,48.26);stub(u['1'],'GND','D',3.81)
cap('C1',86.36,64.77,'10uF / 25V','Capacitor_SMD:C_0603_1608Metric','9V_LDO',desc='Input bulk MLCC,metric1608; exact MPN pending')
cap('C3',55.88,64.77,'100nF / 25V','Capacitor_SMD:C_0603_1608Metric','9V_LDO',desc='Place at LD1117 input; metric1608 MLCC')
esr=resistor('R9',151.13,48.26,'1 ohm','3V3','COUT_BULK',footprint='Resistor_SMD:R_1206_3216Metric',desc='LD1117 ceramic output ESR resistor in capacitor branch only; not in load supply path')
wire(u['2'],esr['1']);label('3V3',132.08,48.26)
wire(esr['2'],(245.11,48.26));label('COUT_BULK',174,48.26)
for ref,x in [('C2',165.1),('C6',191.77),('C7',218.44),('C8',245.11)]:
 p=place(ref,'C',x,62.23,'22uF / 10V','Capacitor_SMD:C_0603_1608Metric',{'1':'COUT_BULK','2':'GND'},mpn='C1608X5R1A226M080AC',maker='TDK',ds='https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X5R1A226M080AC',desc='Metric1608 X5R MLCC; parallel bank behind R9; total effective capacitance at3.3V must remain >=10uF including tolerance')
 wire(p['1'],(x,48.26));junction(x,48.26);stub(p['2'],'GND','D',2.54)
text('U1 TAB = 3V3 (GND 아님) / 9V_SHARED → J2.1\n출력: 1608 MLCC 22 µF × 4 + R9 1 Ω (커패시터 분기에만 직렬)',104.14,76.2,1.27)
for i,(net,x) in enumerate([('9V_SHARED',60.96),('9V_LDO',76.2),('GND',45.72)],1):
 p=place('#FLG'+str(i),'PWR_FLAG',x,82.55,'PWR_FLAG','',{'1':net},props=(x,82.55,x,78.74));stub(p['1'],net,'D',3.81)

text('02  UART 커넥터 / 연결 보드 기준',287.02,29.21,1.905)
port('J3',4,312.42,60.96,'UART / 3.3V OUT',{'1':'3V3','2':'TX_OUT','3':'RX_IN','4':'GND'})
text('J3.2 TX_OUT → 외부 장치 RX\nJ3.3 RX_IN ← 외부 장치 TX\nJ3.1은 전원 출력',287.02,83.82,1.27)
text('03  PPG 수신 / PPG → UART TX_OUT',12.7,100.33,1.905)
port('J2',6,30.48,139.7,'PPG / 6 WIRES',{'1':'9V_SHARED','2':'GND','3':'PPG_TXP','4':'PPG_TXN','5':'PPG_RXP','6':'PPG_RXN'})
text('PPG 기존 J1~J6와 번호대로 연결\nPPG의 12V_IN 표기는 공칭 9V 입력\n차동쌍: TXP/TXN, RXP/RXN',12.7,163.83,1.27)

rx=place('U3','XR33183',215.9,127,'XR33183ESBTR','Adapter:TSOT23-6_MaxLinear',{'1':'3V3','2':'GND','3':'UART_TX_IC','4':'RXN_IC','5':'GND','6':'RXP_IC'},'XR33183ESBTR','MaxLinear','https://www.maxlinear.com/ds/xr33180_xr33181_xr33183_xr33184.pdf','Receiver of PPG TX pair; active-low EN tied to GND',props=(228.6,109.22,228.6,113.03))
for ref,y,nc,ni,pinno in [('R2',121.92,'PPG_TXP','RXP_IC','6'),('R3',132.08,'PPG_TXN','RXN_IC','4')]:
 rp=resistor(ref,165.1,y,'22',nc,ni);wire((101.6,y),rp['1']);label(nc,101.6,y);wire(rp['2'],rx[pinno]);label(ni,177.8,y)
rr=resistor('R1',139.7,127,'120 / 1%','PPG_TXP','PPG_TXN',True,desc='Receiving-end termination; match existing PPG120ohm architecture')
wire(rr['1'],(139.7,121.92));wire(rr['2'],(139.7,132.08));junction(139.7,121.92);junction(139.7,132.08)
stub(rx['1'],'3V3','U',2.54);stub(rx['2'],'GND','D',2.54);stub(rx['5'],'GND','L',5.08)
rp=resistor('R7',279.4,127,'100','UART_TX_IC','TX_OUT');wire(rx['3'],rp['1']);label('UART_TX_IC',248.92,127);stub(rp['2'],'TX_OUT','R',7.62)
d=place('D1','SM712',119.38,156.21,'CDSOT23-SM712','Package_TO_SOT_SMD:SOT-23',{'1':'PPG_TXP','2':'PPG_TXN','3':'GND'},'CDSOT23-SM712','Bourns','https://www.bourns.com/pdfs/CDSOT23-SM712.pdf','Two-line RS422 TVS, pins1/2 signal,pin3GND; connector-side of series resistors',props=(127,146.05,127,149.86))
stub(d['1'],'PPG_TXP','L',5.08);stub(d['2'],'PPG_TXN','L',5.08);stub(d['3'],'GND','D',2.54)
shunt('D3',320.04,152.4,'TX_OUT')
text('TVS 접점 → 직렬저항 → IC\n120 Ω은 이 수신쌍에만 배치',180.34,158.75,1.27)

text('04  PPG 송신 / UART RX_IN → PPG',12.7,190.5,1.905)
tx=place('U2','XR33194',215.9,218.44,'XR33194ESBTR','Adapter:TSOT23-6_MaxLinear',{'1':'UART_RX_IC','2':'3V3','3':'3V3','4':'TXN_IC','5':'GND','6':'TXP_IC'},'XR33194ESBTR','MaxLinear','https://www.maxlinear.com/ds/xr33193_xr33194_xr33195.pdf','Always enabled full-duplex driver; outputs go to PPG RXP/RXN',props=(228.6,200.66,228.6,204.47))
rp=resistor('R8',125.73,218.44,'100','RX_IN','UART_RX_IC');stub(rp['1'],'RX_IN','L',12.7);wire(rp['2'],tx['1']);label('UART_RX_IC',168.91,218.44)
pull=resistor('R6',160.02,207.01,'10k','3V3','UART_RX_IC',True);stub(pull['1'],'3V3','U',2.54);wire(pull['2'],(160.02,218.44));junction(160.02,218.44)
stub(tx['2'],'3V3','U',2.54);stub(tx['3'],'3V3','L',5.08);stub(tx['5'],'GND','D',2.54)
for ref,y,ni,nc,pinno in [('R4',213.36,'TXP_IC','PPG_RXP','6'),('R5',223.52,'TXN_IC','PPG_RXN','4')]:
 rp=resistor(ref,279.4,y,'22',ni,nc);wire(tx[pinno],rp['1']);label(ni,248.92,y);stub(rp['2'],nc,'R',10.16)
d=place('D2','SM712',345.44,236.22,'CDSOT23-SM712','Package_TO_SOT_SMD:SOT-23',{'1':'PPG_RXP','2':'PPG_RXN','3':'GND'},'CDSOT23-SM712','Bourns','https://www.bourns.com/pdfs/CDSOT23-SM712.pdf','Transmit pair cable-side protection; far-end termination exists on PPG',props=(355.6,226.06,355.6,229.87))
stub(d['1'],'PPG_RXP','L',5.08);stub(d['2'],'PPG_RXN','L',5.08);stub(d['3'],'GND','D',2.54)
shunt('D4',104.14,246.38,'RX_IN')
cap('C4',205.74,254,'100nF / 25V','Capacitor_SMD:C_0603_1608Metric','3V3',desc='U2 VCC local bypass; metric1608 MLCC')
cap('C5',264.16,254,'100nF / 25V','Capacitor_SMD:C_0603_1608Metric','3V3',desc='U3 VCC local bypass; metric1608 MLCC')
text('C4는 U2, C5는 U3 전원핀 근처 배치. GND 공통.\nPPG RXP/RXN의 120 Ω 종단은 PPG 보드에 이미 있음.',12.7,271.78,1.27)

# Four pinless NPTH mounting holes; appended to preserve every existing item UUID.
text('05  고정홀 / 기구 가공',345.44,105.41,1.524)
for ref,x,y in [('H1',350.52,121.92),('H2',382.27,121.92),('H3',350.52,149.86),('H4',382.27,149.86)]:
 place(ref,'MountingHole_3mm',x,y,'Ø3.0 mm NPTH','Adapter:MountingHole_3mm_Clearance11mm',{},
  desc='기구 가공 항목: Ø3.0 mm 비도금 관통 고정홀(NPTH), 부품 실장 없음; 머리 조립 여유 Ø11 mm',
  props=(x-1.27,y-5.08,x-7.62,y+5.08))
text('고정홀 4 × Ø3.0 mm NPTH\nPCB 52 × 25 mm / 홀 피치 39 × 12 mm\n머리 조립 여유 Ø11 mm',345.44,166.37,1.27)

HERE.mkdir(exist_ok=True)
sch=f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0") (uuid "{ROOT}") (paper "A3") (title_block (title "PPG UART adapter") (date "2026-10-08") (rev "0.1") (company "MVP-PPG") (comment 1 "9V shared / LD1117 3.3V / full-duplex RS-422")) (lib_symbols '+ '\n'.join(LIB.values())+')\n'+'\n'.join(items)+'\n(sheet_instances (path "/" (page "1"))))\n'
(HERE/(NAME+'.kicad_sch')).write_text(sch,encoding='utf-8')
lib='(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+'\n'.join(v.replace('"Adapter:'+n+'"','"'+n+'"',1) for n,v in LIB.items())+'\n)\n'
(HERE/'Adapter.kicad_sym').write_text(lib,encoding='utf-8')
(HERE/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Adapter")(type "KiCad")(uri "${KIPRJMOD}/Adapter.kicad_sym")(options "")(descr "PPG adapter local symbols")))\n')
(HERE/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Adapter")(type "KiCad")(uri "${KIPRJMOD}/Adapter.pretty")(options "")(descr "PPG adapter local footprints")))\n')
project=HERE/(NAME+'.kicad_pro')
if not project.exists():project.write_text(json.dumps({'meta':{'filename':NAME+'.kicad_pro','version':1},'board':{'design_settings':{'defaults':{'board_outline_line_width':.05}}},'text_variables':{}},indent=2)+'\n')
pretty=HERE/'Adapter.pretty';pretty.mkdir(exist_ok=True)
for fname in ['TSOT23-6_MaxLinear.kicad_mod','TI_DPY0002A_1x0.6.kicad_mod']:shutil.copy2(PARENT/'SleepBud.pretty'/fname,pretty/fname)
for n in [2,4,6]:
 name=f'WirePads_1x{n:02d}_P1.8mm_D1.2';xmax=(n-1)*1.8
 fp=f'(footprint "{name}" (version 20250108) (generator "pcbnew") (layer "F.Cu") (descr "Wire solder pads D1.2mm P1.8mm, no paste, top view pin order") (attr smd exclude_from_bom) (property "Reference" "REF**" (at {xmax/2} -1.7 0) (layer "F.SilkS") {fx(1)}) (property "Value" "{name}" (at {xmax/2} 1.7 0) (layer "F.Fab") {fx(1)}) (fp_rect (start -.85 -.85) (end {xmax+.85} .85) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd")) '
 fp+=' '.join(f'(pad "{i+1}" smd {"rect" if i==0 else "circle"} (at {i*1.8} 0) (size 1.2 1.2) (layers "F.Cu" "F.Mask"))' for i in range(n))+')\n'
 (pretty/(name+'.kicad_mod')).write_text(fp)
(HERE/'design_manifest.json').write_text(json.dumps({'root_uuid':ROOT,'project':NAME,'components':COMP},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (HERE/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','MPN','Manufacturer','Footprint','Datasheet','Voltage','Tolerance','Dielectric','Description'])
 for r,c in COMP.items():
  if not r.startswith('#'):w.writerow([r,c['value'],c['mpn'],c['manufacturer'],c['footprint'],c['datasheet'],c['voltage'],c['tolerance'],c['dielectric'],c['description']])
print(HERE/(NAME+'.kicad_sch'))

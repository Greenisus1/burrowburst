"""Original RGB sprites, drawn with ANSI foreground/background half-blocks.
No fonts, downloaded art, terminal image protocols or third-party libraries.
"""
import os
PALETTE={'.':None,'K':(14,20,36),'Y':(255,205,62),'O':(240,140,40),'S':(255,190,135),'B':(46,169,235),'W':(235,248,255),'D':(35,69,109),'P':(232,97,179),'G':(107,224,126),'R':(245,77,87),'V':(142,115,225),'T':(132,157,181)}
ART={
 'player':('..WWWW..','.WWBBWW.','.WKSSKW.','..WWWW..','.WWBBWYY','WWBWWBYY','..WBBW..','.WW..WW.'),
 'alien':('..RRRR..','.RRRRRR.','RRWWWWRR','RWKWWKWR','RRWWWWRR','RRRRRRRR','.RRRRRR.','..D..D..'),
 'bug':('...G.G..','..GGGGG.','GGGWKGGG','.GGGGGG.','..GWWGG.','.GGGGGG.','GG.GG.G.','...G..G.'),
 'bat':('..RRRR..','.RRRRRR.','RRWWWWRR','RWKWWKWR','RRWWWWRR','RRRRRRRR','.RRRRRR.','..D..D..'),
 'ghost':('..WWWW..','.WWWWWW.','WWDWWDWW','WWKWWKWW','WWWWWWWW','WWWWWWWW','W.WWW.W.','........'),
 'rock':('...TT...','..TTTT..','.TTWWTT.','TTWWTTTD','TTTTTTDD','.TTTTDD.','..DDDD..','........'),
 'warning':('...YY...','..YYYY..','..YKKY..','.YYKKYY.','.YYYYYY.','YYYKKYYY','YYYYYYYY','........'),
 'fall':('O..YY..O','.OYYYYO.','..ORRO..','YYRWWRYY','YYRWWRYY','..ORRO..','.OYYYYO.','O..YY..O'),
 'inflated':('..PPPP..','.PPWWPP.','PPWWWWPP','PPWKKWPP','PPWKKWPP','PPWWWWPP','.PPWWPP.','..PPPP..')}
def supported():return os.environ.get('COLORTERM','').lower() in ('truecolor','24bit') or 'direct' in os.environ.get('TERM','').lower()
def sprite(name,width,height):
 art=ART[name]
 return [[PALETTE[art[min(7,(y*8+4)//height)][min(7,(x*8+4)//width)]] for x in range(width)] for y in range(height)]
def rgb(c,background=False):return '\x1b['+('48' if background else '38')+';2;'+ ';'.join(map(str,c))+'m'
def camera(player,width=16,height=10):
 return min(32-width,max(0,player[0]-width//2)),min(19-height,max(0,player[1]-height//2))
def frame(g,w,h):
 # Zoomed tracking viewport provides enough pixel rows for recognizable custom art.
 vw=min(12,g.W);vh=min(8,g.H);cw=max(2,min(8,(w-4)//vw));ch=max(1,min(4,(h-7)//vh));pw=cw*vw;ph=ch*vh*2
 cx,cy=camera(g.p,vw,vh);ox=(w-pw)//2;oy=3;canvas=[]
 for y in range(ph):
  row=[]
  for x in range(pw):
   q=(cx+x//cw,cy+y//(ch*2));depth=q[1]
   base=(118,77,31) if depth<7 else (85,43,76) if depth<13 else (91,36,41)
   if q not in g.dirt:base=(13,23,41)
   elif (x+3*y)%11==0:base=tuple(min(255,v+22) for v in base)
   row.append(base)
  canvas.append(row)
 def stamp(q,name):
  x,y=q[0]-cx,q[1]-cy
  if not (0<=x<vw and 0<=y<vh):return
  art=sprite(name,cw,ch*2)
  for yy,row in enumerate(art):
   for xx,c in enumerate(row):
    if c is not None:canvas[y*ch*2+yy][x*cw+xx]=c
 for r in g.rocks:
  if not r['dead']:stamp(r['p'],'fall' if r['fall'] else 'warning' if r['wait'] else 'rock')
 for e in g.enemies:stamp(e['p'],'inflated' if e['inflate'] else 'ghost' if e['ghost'] else ('alien','bug','bat')[e['kind']])
 for q,t in g.fx:
  x,y=q[0]-cx,q[1]-cy
  if 0<=x<vw and 0<=y<vh:
   for xx in range(cw):canvas[y*ch*2+ch][x*cw+xx]=(133,255,151)
 stamp(g.p,'player')
 # Facing indicator at the sprite edge stays visible at small zoom sizes.
 x,y=g.p[0]-cx,g.p[1]-cy;dx,dy=((0,-1),(1,0),(0,1),(-1,0))[g.face]
 canvas[y*ch*2+max(0,min(ch*2-1,ch+dy*(ch-1)))][x*cw+max(0,min(cw-1,cw//2+dx*(cw//2)))]=(255,255,255)
 out=[]
 for y in range(0,ph,2):
  out.append(f'\x1b[{oy+y//2+1};{ox+1}H');fg=bg=None
  for x in range(pw):
   a,b=canvas[y][x],canvas[y+1][x]
   if a!=fg:out.append(rgb(a));fg=a
   if b!=bg:out.append(rgb(b,True));bg=b
   out.append('▀')
 out.append('\x1b[0m');return ''.join(out),(cx,cy,vw,vh)

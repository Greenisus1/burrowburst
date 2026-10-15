#!/usr/bin/env python3
"""Burrowburst: original terminal digging arcade, standard library only."""
import curses,json,os,random,time
from collections import deque
from pathlib import Path
from ui import put,run
VERSION='1.1.0'
RECORD=Path.home()/'.local/share/burrowburst/best.json'
DIRS=((0,-1),(1,0),(0,1),(-1,0))
class Game:
 W=32;H=19
 def __init__(self,seed=None):
  self.rng=random.Random(seed);self.score=0;self.lives=3;self.level=0;self.over=False;self.timer=0;self.cool=0;self.invulnerable=0;self.fx=[];self.message='Dig tunnels. Face a creature and tap Space to pump!';self.new_level()
 def new_level(self):
  self.level+=1;self.dirt={(x,y) for x in range(self.W) for y in range(1,self.H)};self.p=(self.W//2,1);self.face=2;self.enemies=[];self.rocks=[];self.fx=[]
  for y in range(7):self.dirt.discard((self.W//2,y))
  for i in range(min(10,3+self.level)):
   x=4+(i%4)*7;y=7+(i//4)*4
   for xx in range(x-1,x+2):self.dirt.discard((xx,y))
   self.enemies.append(dict(p=(x,y),inflate=0,decay=0,kind=i%3,ghost=False))
  for p in ((7,4),(24,5),(13,11),(27,14)):
   self.dirt.discard(p);self.rocks.append(dict(p=p,wait=0,fall=False,dead=False,hits=0))
  self.timer=0;self.cool=0;self.invulnerable=1.5
 def blocked(self,p):return any(r['p']==p and not r['dead'] for r in self.rocks)
 def move(self,d):
  if self.over:return
  self.face=d;dx,dy=DIRS[d];p=(self.p[0]+dx,self.p[1]+dy)
  if 0<=p[0]<self.W and 0<=p[1]<self.H and not self.blocked(p):
   self.p=p
   if p in self.dirt:self.dirt.remove(p);self.score+=1
  self.collide()
 def ray(self,p,d,n):
  x,y=p;dx,dy=DIRS[d];out=[]
  for i in range(n):
   x+=dx;y+=dy;q=(x,y)
   if not (0<=x<self.W and 0<=y<self.H) or q in self.dirt or self.blocked(q):break
   out.append(q)
  return out
 def pump(self):
  if self.over or self.cool>0:return
  self.cool=.17;ray=self.ray(self.p,self.face,4);self.fx=[(p,.12) for p in ray]
  for p in ray:
   e=next((e for e in self.enemies if e['p']==p),None)
   if e:
    e['inflate']+=1;e['decay']=1.2
    if e['inflate']>=4:self.enemies.remove(e);self.score+=100+20*self.level;self.message='POP! +'+str(100+20*self.level)
    else:self.message='Pump '+str(e['inflate'])+'/4 - keep pumping!'
    break
 def hurt(self,reason):
  if self.invulnerable>0 or self.over:return
  self.lives-=1;self.message=reason
  if self.lives<=0:self.over=True;self.message='GAME OVER - R restarts';return
  self.p=(self.W//2,0);self.face=2;self.invulnerable=3
 def collide(self):
  if any(e['p']==self.p and e['inflate']==0 for e in self.enemies):self.hurt('Caught! Back to the surface.')
 def path(self,start):
  q=deque([(start,None)]);seen={start}
  while q:
   p,first=q.popleft()
   if p==self.p:return first
   for dx,dy in DIRS:
    n=(p[0]+dx,p[1]+dy)
    if 0<=n[0]<self.W and 0<=n[1]<self.H and n not in self.dirt and n not in seen and not self.blocked(n):seen.add(n);q.append((n,first or n))
  return None
 def tick(self,dt):
  if self.over:return
  dt=min(.1,max(0,dt));self.cool=max(0,self.cool-dt);self.invulnerable=max(0,self.invulnerable-dt);self.timer+=dt;self.fx=[(p,t-dt) for p,t in self.fx if t>dt]
  for r in self.rocks:
   if r['dead']:continue
   x,y=r['p'];below=(x,y+1)
   if y==self.H-1 or self.blocked(below):
    if r['fall']:r['dead']=True
    continue
   if below not in self.dirt or r['fall']:
    r['wait']+=dt
    threshold=.09 if r['fall'] else .65
    if r['wait']>=threshold:
     r['fall']=True;r['wait']=0;r['p']=below;self.dirt.discard(below)
     for e in list(self.enemies):
      if e['p']==below:self.enemies.remove(e);r['hits']+=1;self.score+=250*r['hits'];self.message='Rock crush! +'+str(250*r['hits'])
     if self.p==below:self.hurt('Crushed by a rock!')
   else:r['wait']=0
  for e in self.enemies:
   if e['inflate']:
    e['decay']-=dt
    if e['decay']<=0:e['inflate']-=1;e['decay']=.7
  if self.timer>=max(.16,.6-self.level*.025):
   self.timer=0
   for e in self.enemies:
    if e['inflate']:continue
    n=self.path(e['p']);e['ghost']=n is None
    if n is None:
     x,y=e['p'];px,py=self.p
     n=(x+(1 if px>x else -1 if px<x else 0),y) if abs(px-x)>abs(py-y) else (x,y+(1 if py>y else -1 if py<y else 0))
     if self.blocked(n):continue
    if n is not None:e['p']=n
   self.collide()
  if not self.enemies:self.message='Stage cleared! Dig deeper.';self.new_level()
def best():
 try:
  if RECORD.is_symlink():return 0
  return max(0,int(json.loads(RECORD.read_text()).get('best',0)))
 except (OSError,ValueError,TypeError,AttributeError):return 0
def save(score):
 try:
  if any(p.is_symlink() for p in [RECORD,*RECORD.parents]):return False
  RECORD.parent.mkdir(parents=True,exist_ok=True,mode=0o700);tmp=RECORD.with_suffix('.tmp')
  fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump({'best':max(best(),score)},f)
  tmp.replace(RECORD);return True
 except (OSError,ValueError):return False
def setup_colors():
 if not curses.has_colors():return False
 curses.start_color();curses.use_default_colors()
 # The first six preserve familiar role indices; 256-color terminals get layered earth.
 basic=[(3,-1),(6,-1),(5,-1),(1,-1),(2,-1),(7,-1),(3,-1),(7,-1),(7,-1),(2,-1),(5,-1),(1,-1)]
 rich=[(180,94),(51,17),(175,53),(174,52),(118,17),(231,17),(220,17),(153,17),(110,17),(118,17),(213,17),(208,17)]
 for i,(fg,bg) in enumerate(rich if curses.COLORS>=256 else basic,1):curses.init_pair(i,fg,bg)
 return True

EMOJI={'player':'👷','rock':'🪨','warning':'⚠','fall':'💥','ghost':'👻','enemies':('👾','🐛','🦇')}
def display_width(text):
 import unicodedata
 return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in text)
def pad_cell(text,width):
 out='';used=0
 for c in text:
  n=display_width(c)
  if used+n>width:break
  out+=c;used+=n
 return out+' '*(width-used)
def default_emoji():
 import locale
 return 'UTF-8' in locale.getpreferredencoding(False).upper() and os.environ.get('TERM','')!='linux' and '--ascii' not in __import__('sys').argv

def play(s):
 s.timeout(25);g=Game();last=time.monotonic();paused=False;recorded=False;high=best();note='';emoji=default_emoji()
 palette=setup_colors()
 def color(i):return curses.color_pair(i) if palette else 0
 while True:
  key=s.getch();now=time.monotonic();dt=now-last;last=now;h,w=s.getmaxyx();s.erase()
  if key in (27,ord('q'),ord('Q')):return
  if key in (ord('r'),ord('R')):g=Game();paused=False;recorded=False;note=''
  if key in (ord('p'),ord('P')):paused=not paused
  if key in (ord('e'),ord('E')):emoji=not emoji
  if h<26 or w<70:put(s,1,1,'Resize to 70x26 or larger. Game paused. Q quits.');s.refresh();continue
  if not paused and not g.over:
   mapping={curses.KEY_UP:0,curses.KEY_RIGHT:1,curses.KEY_DOWN:2,curses.KEY_LEFT:3,ord('w'):0,ord('d'):1,ord('s'):2,ord('a'):3,ord('W'):0,ord('D'):1,ord('S'):2,ord('A'):3}
   if key in mapping:g.move(mapping[key])
   if key==ord(' '):g.pump()
   g.tick(dt)
  if g.over and not recorded:note='Best saved.' if save(g.score) else 'Could not save best.';recorded=True;high=max(high,best())
  put(s,0,2,'BURROWBURST  |  STAGE '+str(g.level)+'  |  SCORE '+str(g.score)+'  |  LIVES '+str(g.lives),color(7)|curses.A_BOLD)
  put(s,1,2,('PAUSED  |  ' if paused else '')+(g.message if not paused else 'P to resume')+'  |  BEST '+str(high),color(8))
  cw=max(2,(w-4)//g.W);ox=(w-cw*g.W)//2;oy=3;bh=h-7
  def tile(p,text,attr,sprite=False):
   x,y=p;top=y*bh//g.H;bottom=(y+1)*bh//g.H
   for yy in range(top,bottom):
    content=pad_cell(text,cw) if not sprite or yy==top+(bottom-top-1)//2 else ' '*cw
    put(s,oy+yy,ox+x*cw,content,attr)
  for y in range(g.H):
   for x in range(g.W):tile((x,y),('·' if emoji else '.')*cw if (x,y) in g.dirt else ' '*cw,color(1 if y<7 else 3 if y<13 else 4) if (x,y) in g.dirt else color(9))
  for r in g.rocks:
   if not r['dead']:
    sprite=EMOJI['fall' if r['fall'] else 'warning' if r['wait'] else 'rock'] if emoji else '##' if r['fall'] else '><' if r['wait'] else '[]'
    tile(r['p'],sprite,color(6),True)
  for p,t in g.fx:tile(p,('━━' if g.face%2 else '┃ ') if emoji else ('--' if g.face%2 else '||'),color(5)|curses.A_BOLD,True)
  for e in g.enemies:
   sprite=(str(e['inflate'])+'○' if emoji else str(e['inflate'])*2) if e['inflate'] else (EMOJI['ghost'] if e['ghost'] else EMOJI['enemies'][e['kind']]) if emoji else 'oo' if e['ghost'] else ('xx','vv','zz')[e['kind']]
   tile(e['p'],sprite,color(10+e['kind']),True)
  # Helmet, human face and a facing arrow, rather than an anonymous direction marker.
  px,py=g.p;top=py*bh//g.H;bottom=(py+1)*bh//g.H
  tile(g.p,EMOJI['player'] if emoji else '@'+('^','>','v','<')[g.face],color(2)|curses.A_BOLD,True)
  if emoji and cw>=3:
   put(s,oy+top+(bottom-top-1)//2,ox+px*cw+2,('↑','→','↓','←')[g.face],color(2)|curses.A_BOLD)
  if bottom-top>=2:put(s,oy+top,ox+px*cw,('▰ ' if emoji else '=='),color(7)|curses.A_BOLD)
  put(s,h-3,2,'Arrows/WASD dig | Space pump | P pause | R restart | Q quit',color(8))
  put(s,h-2,2,'E sprites: '+('EMOJI' if emoji else 'ASCII')+' | Rocks warn, then fall. Pump 4 times. Ghosts cross dirt.',color(8))
  put(s,h-1,2,note or 'Dig deep. Keep your helmet on. Clear every creature to advance.',color(7));s.refresh()
if __name__=='__main__':
 import sys
 if '--version' in sys.argv:print(VERSION)
 else:raise SystemExit(run(play))

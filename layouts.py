"""Layouts measured from arcade round screenshots, not ROM/game source.
Reference: https://edcollins.com/digdug/ (round images 1a,2,3,4,5,6).
14-column reference grid is expanded to Burrowburst's 32x19 cells.
Tunnels/rocks verified visually; enemies follow the captured positions, not
cycle-exact initial spawn coordinates. Later rounds repeat these adaptations.
"""
LAYOUTS=[
 dict(tunnels=[(6,1,6,8),(5,8,7,8),(1,3,1,7),(9,3,12,3),(2,11,5,11),(9,10,9,14)],rocks=[(4,4),(10,10),(3,12)],red=[(1,4),(10,3),(9,12)],green=[(4,11)]),
 dict(tunnels=[(6,1,6,8),(5,8,7,8),(10,4,12,4),(1,7,3,7),(1,10,1,12),(6,10,8,10),(10,12,12,12)],rocks=[(2,3),(8,4),(12,9),(4,12)],red=[(3,7),(1,10),(6,10)],green=[(10,4),(10,12)]),
 dict(tunnels=[(6,1,6,8),(5,8,7,8),(10,3,12,3),(7,4,7,6),(1,6,3,6),(5,10,5,12),(8,13,10,13)],rocks=[(2,3),(11,7),(3,10),(12,12)],red=[(1,6),(7,6),(5,12)],green=[(12,3),(10,13)]),
 dict(tunnels=[(6,1,6,8),(5,8,7,8),(3,4,5,4),(7,4,7,6),(11,8,11,10),(3,11,5,11),(7,13,9,13)],rocks=[(10,3),(2,5),(11,6),(3,9),(12,12)],red=[(4,4),(7,4),(7,13)],green=[(11,9),(5,11)]),
 dict(tunnels=[(6,1,6,8),(5,8,7,8),(1,4,3,4),(5,4,5,6),(9,3,9,5),(10,7,10,9),(2,10,4,10),(10,11,12,11)],rocks=[(8,3),(12,4),(2,7),(5,11),(10,12)],red=[(9,3),(3,4),(5,4)],green=[(10,7),(4,10),(10,11)]),
 dict(tunnels=[(6,1,6,8),(5,8,7,8),(3,4,5,4),(2,6,2,8),(9,9,11,9),(1,10,3,10),(5,12,7,12)],rocks=[(7,3),(10,7),(6,10),(2,12)],red=[(5,4)],green=[(2,6),(9,9),(3,10),(7,12)])]
def point(p):return round(p[0]*31/13),round(p[1]*18/15)
def build(stage):
 data=LAYOUTS[(stage-1)%len(LAYOUTS)];opened=set()
 for ax,ay,bx,by in data['tunnels']:
  ax,ay=point((ax,ay));bx,by=point((bx,by));n=max(abs(bx-ax),abs(by-ay))
  opened.update((round(ax+(bx-ax)*i/max(1,n)),round(ay+(by-ay)*i/max(1,n))) for i in range(n+1))
 rocks=[point(p) for p in data['rocks']];enemies=[(point(p),kind) for kind,key in ((0,'red'),(1,'green')) for p in data[key]]
 opened.update(rocks);opened.update(p for p,k in enemies)
 return opened,rocks,enemies,point((6,8))
def label(stage):return 'Arcade reference '+str(stage) if stage<=6 else 'Adapted repeat '+str((stage-1)%6+1)
def flowers(cleared,width,ascii=False):
 symbol='*' if ascii else '✿';count=max(0,cleared);room=max(0,(width-22)//2);visible=min(room,count)
 return 'CLEARED '+str(count)+'  '+(symbol+' ')*visible+('+'+str(count-visible) if count>visible else '')

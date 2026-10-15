import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import burrowburst as b
class GameTests(unittest.TestCase):
 def clean(self):
  g=b.Game(1);g.enemies=[];g.rocks=[];g.invulnerable=0;return g
 def test_stage(self):
  g=b.Game(1);self.assertEqual(g.level,1);self.assertEqual(len(g.enemies),4);self.assertEqual(g.lives,3)
 def test_dig(self):
  g=self.clean();g.p=(1,1);g.move(1);self.assertNotIn((2,1),g.dirt);self.assertEqual(g.score,1)
 def test_bounds(self):
  g=self.clean();g.p=(0,0);g.move(0);g.move(3);self.assertEqual(g.p,(0,0))
 def test_rock_blocks(self):
  g=self.clean();g.rocks=[dict(p=(2,1),dead=False)];g.p=(1,1);g.move(1);self.assertEqual(g.p,(1,1))
 def test_pump_pop(self):
  g=self.clean();g.p=(1,1);g.face=1;g.dirt.clear();g.enemies=[dict(p=(3,1),inflate=0,decay=0)]
  for _ in range(4):g.cool=0;g.pump()
  self.assertEqual(g.enemies,[]);self.assertEqual(g.score,120)
 def test_pump_dirt(self):
  g=self.clean();g.p=(1,1);g.face=1;g.enemies=[dict(p=(3,1),inflate=0,decay=0)];g.pump();self.assertEqual(g.enemies[0]['inflate'],0)
 def test_cooldown(self):
  g=self.clean();g.p=(1,1);g.face=1;g.dirt.clear();g.enemies=[dict(p=(2,1),inflate=0,decay=0)];g.pump();g.pump();self.assertEqual(g.enemies[0]['inflate'],1)
 def test_deflate(self):
  g=self.clean();g.enemies=[dict(p=(1,1),inflate=2,decay=.01)];g.tick(.1);self.assertEqual(g.enemies[0]['inflate'],1)
 def test_collision(self):
  g=self.clean();g.enemies=[dict(p=g.p,inflate=0)];g.collide();self.assertEqual(g.lives,2);g.collide();self.assertEqual(g.lives,2)
 def test_gameover(self):
  g=self.clean();g.lives=1;g.hurt('ouch');self.assertTrue(g.over)
 def test_path(self):
  g=self.clean();g.dirt.clear();g.p=(3,1);self.assertEqual(g.path((1,1)),(2,1))
 def test_rock_warning_and_crush(self):
  g=self.clean();g.dirt.clear();g.p=(30,1);g.enemies=[dict(p=(2,3),inflate=2,decay=10),dict(p=(10,10),inflate=2,decay=10)];g.rocks=[dict(p=(2,2),wait=0,fall=False,dead=False,hits=0)]
  for _ in range(6):g.tick(.1)
  self.assertEqual(g.rocks[0]['p'],(2,2));g.tick(.1);self.assertEqual(g.rocks[0]['p'],(2,3));self.assertEqual(g.score,250)
 def test_level_clear(self):
  g=self.clean();g.tick(.1);self.assertEqual(g.level,2)
 def test_record(self):
  with tempfile.TemporaryDirectory() as d,patch.object(b,'RECORD',Path(d)/'r.json'):
   self.assertTrue(b.save(123));self.assertEqual(b.best(),123);b.save(2);self.assertEqual(b.best(),123)
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as d,patch.object(b,'RECORD',Path(d)/'r.json'):
   b.RECORD.symlink_to(Path(d)/'outside');self.assertFalse(b.save(2))
class SpriteTests(unittest.TestCase):
 def test_width(self):
  self.assertEqual(b.display_width('🧑'),2)
  self.assertEqual(b.display_width(b.pad_cell('🧑',3)),3)
 def test_clip(self):
  self.assertEqual(b.pad_cell('🧑',1),' ')
 def test_ascii(self):
  self.assertEqual(b.pad_cell('@>',3),'@> ')
if __name__=='__main__':unittest.main()

class PixelTests(unittest.TestCase):
 def test_art(self):
  import pixelart as p
  for name,rows in p.ART.items():
   self.assertEqual(len(rows),8)
   self.assertTrue(all(len(row)==8 for row in rows),name)
   self.assertTrue(all(c in p.PALETTE for row in rows for c in row))
 def test_resample(self):
  import pixelart as p
  for w,h in ((2,2),(8,8),(7,6)):
   a=p.sprite('player',w,h);self.assertEqual(len(a),h);self.assertTrue(all(len(r)==w for r in a))
 def test_camera(self):
  import pixelart as p
  self.assertEqual(p.camera((0,0),12,8),(0,0));self.assertEqual(p.camera((31,18),12,8),(20,11))
 def test_ansi(self):
  import pixelart as p
  g=b.Game();text,view=p.frame(g,110,32)
  self.assertIn('\x1b[38;2;',text);self.assertIn('\x1b[48;2;',text);self.assertTrue(text.endswith('\x1b[0m'))
  self.assertEqual(view[2:],(12,8))
 def test_sizes(self):
  import pixelart as p
  for w,h in ((70,26),(110,32),(180,60)):
   for q in ((0,0),(31,18),(16,1)):
    g=b.Game();g.p=q;self.assertTrue(p.frame(g,w,h)[0])
 def test_capability(self):
  import pixelart as p
  with patch.dict('os.environ',{'COLORTERM':'truecolor'}):self.assertTrue(p.supported())

class LayoutTests(unittest.TestCase):
 def test_first_round(self):
  g=b.Game();self.assertEqual(sum(e['kind']==1 for e in g.enemies),1);self.assertEqual(len(g.rocks),3)
 def test_reference_counts(self):
  import layouts
  self.assertEqual([(len(d['red']),len(d['green'])) for d in layouts.LAYOUTS],[(3,1),(3,2),(3,2),(3,2),(3,3),(1,4)])
 def test_valid_positions(self):
  import layouts
  for stage in range(1,100):
   opened,rocks,enemies,start=layouts.build(stage)
   for x,y in opened:self.assertTrue(0<=x<32 and 0<=y<19)
   self.assertIn(start,opened)
   self.assertTrue(all(p in opened for p,k in enemies))
   self.assertFalse(set(rocks)&{p for p,k in enemies})
 def test_flower_count(self):
  import layouts
  self.assertEqual(layouts.flowers(3,110).count('✿'),3)
  self.assertIn('+',layouts.flowers(100,70))
 def test_clear_flower(self):
  g=b.Game();g.enemies=[];g.tick(.01);self.assertEqual(g.level-1,1)
 def test_repeat_labeled(self):
  import layouts
  self.assertIn('Adapted repeat',layouts.label(7))

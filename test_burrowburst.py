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

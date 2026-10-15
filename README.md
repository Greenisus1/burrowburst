# Burrowburst

An original fullscreen digging arcade inspired by the old Dig Dug arcade game. Dig tunnels, face creatures and pump them until they pop, or dig out a rock's support and run before it falls. Clear each stage, keep your three lives, and aim for a local best score.

Original name, text art and code. No Namco assets, music or affiliation. A simplified tribute, not an exact port: no fire-breathing enemies, bonus vegetables or original stage layouts. Built with AI assistance from my design.

## Controls

Arrows or WASD dig and face that way. Space pumps along up to four open tunnel cells. Four pumps pop a creature; inflation wears off if you wait. Hold Space to repeat (0.17 second cooldown). P pauses, R starts a new run, Q or Esc quits. Letter controls accept either case.

Creatures follow open tunnels and ghost through dirt when no open path exists. Inflated creatures cannot move or hurt you. Rocks marked `[]` become `><` for 0.65 seconds after you dig below them, then `##` as they fall. Rocks can crush you too. Each crushed creature scores 250 times the number crushed by that rock. A pump pop scores 100 plus 20 per stage; digging new earth scores 1.

Runs in a plain SSH terminal, no desktop, internet, account, paid API or setup. Minimum 70x26, scales across larger terminals. A small window pauses play. SSH latency and keyboard repeat affect controls. Pause/restart/quit are available throughout.

## Install

Pi App Store -> Games -> Burrowburst. The installer adds Python/curses using apt, apk or pacman when missing. That needs root; Arch keeps its normal system-upgrade confirmation. No pip packages.

    bash app-store.sh INSTALL
    bash app-store.sh RUN
    python3 -m unittest -v

Best score is local at `~/.local/share/burrowburst/best.json`, saved on game over, never sent anywhere. Restarting or quitting a run discards that run's unsaved score. Storage failures are shown. Concurrent sessions do not form a shared leaderboard.

## Tests

Automated tests cover digging, boundaries, pump range/obstacles/cooldown/pop/decay, lives, paths, falling rocks, stage progression and local records. Interactive terminal tests cover input, pause, resize and clean exit. See release verification for target hardware status.

MIT license, copyright 2026 Greenisus1.

## 1.1.0 visual update

Emoji sprites include a helmeted worker, alien/bug/bat creatures, ghosts and rocks. A 256-color terminal gets solid ochre, plum and red earth layers with dark blue tunnels. Basic-color and monochrome terminals remain supported. Gameplay rules, scores and controls are unchanged.

E toggles emoji/ASCII at any time; use `python3 burrowburst.py --ascii` to start with the compact ASCII sprites. Linux console or non-UTF-8 sessions default to ASCII. No joined emoji sequences or skin-tone variants are used. Padding counts wide characters instead of assuming one character equals one cell. Terminal fonts and emoji-width tables vary, so automatic detection cannot guarantee the client display: press E if sprites look misplaced or like boxes. Color emoji requires support on the device displaying the SSH session, not a font installed on the Pi. There are no new runtime dependencies.

Test evidence: 18 local unit tests, separate real-PTY emoji/ASCII runs with E/e toggle, resize, pause/restart and uppercase Q restore checks. Host rendering previews use Noto Color Emoji; actual Pi/Mac client fonts may differ. The release passed 18 tests and both emoji/ASCII PTY checks on a real aarch64 Raspberry Pi before publication.

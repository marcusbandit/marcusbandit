#!/bin/bash
# frame.sh <svg> <background> <time_ms> <out.png> <window_w> <window_h>
# Renders one SVG at a fixed animation time in headless Chrome. Freezes both CSS
# animations and SMIL, so frames are deterministic.
svg=$1 bg=$2 t=$3 out=$4 w=$5 h=$6
html=$(mktemp --suffix=.html)
{
  echo "<body style='background:$bg;margin:20px'>"
  cat "$svg"
  echo "<script>requestAnimationFrame(()=>{document.querySelectorAll('svg').forEach(s=>{if(s.pauseAnimations){s.pauseAnimations();s.setCurrentTime($t/1000)}});document.getAnimations().forEach(a=>{a.pause();a.currentTime=$t});});</script></body>"
} > "$html"
google-chrome-stable --headless=new --disable-gpu --hide-scrollbars --window-size=$w,$h --virtual-time-budget=400 --screenshot="$out" "file://$html" 2>/dev/null
rm -f "$html"

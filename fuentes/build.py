W='/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/work/'
css=open(W+'orig.css').read()
css=css.replace("padding-inline:16px;padding-block:20px 40px","padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:20px 40px").replace("--bg:#f3f5f8","--card:#ffffff; --good:#15803d; --bad:#c2410c; --bg:#f3f5f8").replace(".mapsvg path,.mapsvg rect.sqr{stroke:var(--card)",".mapsvg path,.mapsvg rect.sqr{stroke:var(--surface)")
css=css.replace("--live:#fb923c;","--live:#fb923c; --good:#4ade80; --bad:#fb923c;")
c=open(W+'extra.css').read()
head='<meta name="claude:viewport-fit-sides" content="cover">\n<title>Poll of polls 29N</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">\n<style>\n'+css+c+'\n</style>\n'
js=open(W+'data.js').read()+open(W+'map.js').read()+'\n'+open(W+'engine.js').read()+'\n'+open(W+'ui.js').read()
html=head+open(W+'body.html').read()+'<script>\n'+js+'\n</script>\n'
open('/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/poll_of_polls_29N.html','w').write(html)
print(len(html))

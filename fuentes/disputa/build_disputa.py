W='/tmp/claude-0/-home-claude/eea0bbaf-2db4-5718-a729-17707b9905cb/scratchpad/work/'
css=open(W+'orig.css').read()
css=css.replace("padding-inline:16px;padding-block:20px 40px","padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:20px 40px").replace("--bg:#f3f5f8","--card:#ffffff; --bg:#f3f5f8")
c=open(W+'extra.css').read()+open(W+'disputa_extra.css').read()
head='<meta name="claude:viewport-fit-sides" content="cover">\n<title>Escaños en disputa 29N</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">\n<style>\n'+css+c+'\n</style>\n'
html=head+open(W+'disputa_body.html').read()+'<script>\n'+open(W+'map.js').read()+'\nconst DS='+open(W+'../disputa.json').read()+';\n'+open(W+'disputa.js').read()+'\n</script>\n'
open('/tmp/d.html','w').write(html)

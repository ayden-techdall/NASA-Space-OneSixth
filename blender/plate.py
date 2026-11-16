"""Camera-space design shared by the native scene and the portable proof renderer."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT/'scene_data.json').read_text())
W,H = 1920,1080
INK='#121b1e'; PANEL='#142028'; PAPER='#f3eedf'; WHITE='#faf5e5'
MUTED='#505e5e'; SILVER='#bac8c7'; AMBER='#ffae72'; RUST='#9a4528'; RULE='#c8c8b9'
def plate():
    shapes=[]
    def rect(name,box,color): shapes.append(('rect',name,box,color))
    def line(name,xy,color,w=2): shapes.append(('line',name,xy,color,w))
    def text(name,x,y,s,n,face,color): shapes.append(('text',name,x,y,s,n,face,color))
    def dot(name,x,y,r,color): shapes.append(('dot',name,x,y,r,color))
    def track(name,x,y,width,lo,hi,domain,ink,fill):
        a=x+width*lo/domain; b=x+width*hi/domain
        line(name+' rule',[(x,y),(x+width,y)],RULE,2)
        rect(name+' range',(a,y-6,b,y+6),fill)
        for v in [a,b]: line(name+' endpoint',[(v,y-10),(v,y+10)],ink,3)
    h=DATA['headline']; air=DATA['atmospheres']; hab=air['habitat']; norm=air['earth_air']['psia']
    lo,hi=h['habitat_forecast_range']; central=h['habitat_forecast_central']; ml,mh=h['moon_limit_14_7_psia_measured_bracket']
    e=[o['o2'] for o in DATA['evidence'] if o['kind']=='earth_limit']
    rect('Ivory page',(0,0,W,H),PAPER); rect('Night field',(0,0,771,H),PANEL)
    line('Left masthead',[(59,94),(711,94)],'#576268',2)
    text('Project',59,44,'ONE–SIXTH',25,'bold',WHITE)
    text('Field',464,48,'LUNAR FIRE STUDY',18,'mono',SILVER)
    text('Title top',58,130,'The lunar',80,'serif',WHITE)
    text('Title bottom',58,220,'burn limit',91,'italic',WHITE)
    shapes.append(('image','Illustrative lunar relief',(105,334,662,891),'renders/lunar_relief.png'))
    for x,y in [(74,407),(700,407),(74,810),(700,810)]:
        line('Registration cross',[(x-7,y),(x+7,y)],'#8a9798',1)
        line('Registration cross',[(x,y-7),(x,y+7)],'#8a9798',1)
    line('Specimen rule',[(59,930),(711,930)],'#576268',2)
    text('Subject',59,955,'THIN CELLULOSE TISSUE',24,'mono',WHITE)
    text('Mode',59,1003,'Downward flame spread in still air',29,'regular',SILVER)
    text('Illustration credit',198,889,'Illustrative lunar relief',19,'mono',SILVER)
    version, date = DATA['meta']['forecast_version'].split(', registered ')
    text('Version',832,48,'REGISTERED FORECAST  /  '+version.upper(),23,'mono',RUST)
    line('Right masthead',[(832,94),(1855,94)],RULE,2)
    text('Question',828,132,'How little oxygen keeps',64,'serif',INK)
    text('Question second line',828,206,'the paper burning?',64,'serif',INK)
    text('Condition',833,318,f'LUNAR GRAVITY    /    HABITAT PRESSURE  {hab["psia"]:g} PSIA',24,'mono',MUTED)
    text('Headline',824,375,f'{lo:.1f}–{hi:.1f}%',106,'serif',RUST)
    text('Headline detail',833,506,f'Forecast oxygen limit. Central estimate near {central:.1f}%.',29,'regular',INK)
    x,span,domain=860,941,40
    y=636
    for value in range(0,41,10):
        xx=x+span*value/domain
        line('Scale tick',[(xx,y-8),(xx,y+12)],MUTED,2)
        text('Scale value',xx-9,y+25,str(value),20,'mono',MUTED)
    track('Forecast',x,y,span,lo,hi,domain,RUST,RUST)
    xx=x+span*central/domain
    dot('Central estimate',xx,y,5,WHITE)
    xx=x+span*hab['o2']/domain
    line('Habitat reference',[(xx,y-45),(xx,y+8)],INK,3)
    dot('Habitat reference point',xx,y,7,INK)
    text('Atmosphere',xx-191,y-86,f'{hab["o2"]:g}% planned habitat air',26,'bold',INK)
    text('Axis units',833,714,'Oxygen by volume (%)',24,'regular',MUTED)
    line('Evidence divider',[(832,777),(1855,777)],RULE,2)
    text('Earlier evidence',833,812,f'MEASURED AT {norm:g} PSIA',23,'mono',MUTED)
    text('Aircraft result',830,863,f'{ml:g}–{mh:g}%',51,'serif',INK)
    text('Aircraft label',833,938,'Lunar gravity · aircraft bracket',25,'regular',MUTED)
    text('Earth result',1350,863,f'{e[0]:g}%  /  {e[1]:g}%',48,'serif',INK)
    text('Earth label',1352,938,'Earth · two reported limits',25,'regular',MUTED)
    line('Colophon rule',[(832,991),(1855,991)],RULE,2)
    text('Colophon',833,1014,'AYDEN TINDALL  /  CHARLES ANDRADE',19,'mono',MUTED)
    text('Dateline',1613,1014,date.upper(),19,'mono',MUTED)
    return shapes

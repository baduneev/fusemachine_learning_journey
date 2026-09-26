"""Regenerate the supplied static diagram (optional dependency: matplotlib)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root=Path(__file__).resolve().parents[1]
fig, ax=plt.subplots(figsize=(15,10.8),dpi=160)
ax.set_xlim(0,15); ax.set_ylim(0,10.8); ax.axis('off')
fig.patch.set_facecolor('white')
navy='#183b5b'; ink='#22364b'; green='#187557'

def box(x,y,w,h,title,body='',color='#eef3f8',dark=False):
 ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.08,rounding_size=0.12',facecolor=color,edgecolor='#b8c7d5',linewidth=1.1))
 ax.text(x,y+(0.18 if body else 0),title,ha='center',va='center',fontsize=12,fontweight='bold',color='white' if dark else ink)
 if body: ax.text(x,y-0.22,body,ha='center',va='center',fontsize=10.5,linespacing=1.5,color='white' if dark else ink)

def arrow(start,end,label='',color='#567086',rad=0):
 ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,linewidth=1.6,color=color,connectionstyle=f'arc3,rad={rad}'))
 if label: ax.text((start[0]+end[0])/2,(start[1]+end[1])/2+0.13,label,ha='center',va='center',fontsize=9,color=color,bbox=dict(facecolor='white',edgecolor='none',pad=2))

ax.text(.6,10.35,'WEEK 16  /  AGENTIFY THE ASSISTANT',fontsize=21,fontweight='bold',color=navy)
ax.text(.6,9.97,'Model-controlled decisions • Bounded evidence • Verifiable citations',fontsize=12,color='#627488')
box(7.3,9.1,3.4,.6,'USER QUESTION')
box(7.3,7.9,5.8,1.0,'SINGLE GEMINI AGENT','Choose the next action from the last observation',navy,True)
arrow((7.3,8.72),(7.3,8.48))
for x in [2.7,6.1,9.4,12.7]:
 arrow((7.3,7.33),(x,6.68))
box(2.7,6.1,3.0,1.0,'RETRIEVE EVIDENCE','search_documents\nread_source')
box(6.1,6.1,2.8,1.0,'VERIFY CLAIMS','Source IDs + exact quotes')
box(9.4,6.1,2.7,1.0,'FINISH GATE','Exact verified claims only')
box(12.7,6.1,2.7,1.0,'STOP','Clarify / abstain\n8-step cap / model error','#fff1da')
box(2.7,4.45,3.2,1.15,'DOCUMENT BACKEND','W15 Chroma + reranker\nor lightweight PDF search')
arrow((2.7,5.52),(2.7,5.10))
box(9.4,4.45,2.7,.9,'CITED ANSWER','Verified claims + sources','#e6f3ed')
arrow((9.4,5.52),(9.4,4.98),'Pass')
box(5.0,2.65,6.4,1.25,'BOUNDED CONTEXT','Top 3 results per call; 900 characters per excerpt\nLast 8 evidence items + 3 action summaries','#e6f3ed')
arrow((2.7,3.8),(3.5,3.34),'Evidence / tool error')
arrow((6.1,5.52),(6.1,3.34),'Check result')
# Rejected finalization also returns an observation.
ax.plot([7.97,7.8,7.8],[6.1,6.1,3.55],color='#567086',lw=1.6)
arrow((7.8,3.55),(7.8,3.34))
ax.text(7.8,4.5,'Reject',rotation=90,ha='center',va='center',fontsize=9,color='#567086',bbox=dict(facecolor='white',edgecolor='none',pad=2))
box(11.5,2.65,4.3,1.25,'EXTERNAL TRACE','Full evidence ledger + all decisions\nEvaluation and token accounting','#f5f5f5')
arrow((8.3,2.65),(9.25,2.65))
# Explicit feedback path kept outside all boxes.
ax.plot([1.72,.5,.5,4.32],[2.65,2.65,7.9,7.9],color=green,lw=2.3)
arrow((4.0,7.9),(4.32,7.9),color=green)
ax.text(.69,5.1,'NEXT ITERATION',rotation=90,ha='center',va='center',color=green,fontweight='bold',fontsize=11,bbox=dict(facecolor='white',edgecolor='none',pad=3))
ax.text(.6,1.08,'Grounding limit: exact quote matching checks provenance; the model must still check meaning and contradictions.',fontsize=10.5,color='#52687c')
ax.text(.6,.64,'One decision per iteration. Maximum 8 by default. Full traces stay outside the growing model conversation.',fontsize=10.5,color='#52687c')
fig.tight_layout(pad=.5)
for ext in ['png','svg']:
 fig.savefig(root/'docs'/f'architecture.{ext}',facecolor='white')

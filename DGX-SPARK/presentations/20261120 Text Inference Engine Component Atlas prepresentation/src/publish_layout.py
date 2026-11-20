"""Apply the component views to the existing standalone atlas, retaining its original shell."""
from pathlib import Path
import json

def render_copy(base, here, title, records):
    original = base.parent / "20261117 Text Inference Engine Atlas prepresentation.html"
    page = original.read_text("utf-8")
    def replace(old, new):
        nonlocal page
        if page.count(old) != 1:
            raise ValueError(f"Unexpected original atlas signature: {old[:90]}")
        page = page.replace(old, new, 1)
    def source(name):
        return (here/name).read_text("utf-8-sig")
    replace("<title>"+original.stem+"</title>", "<title>"+title+"</title>")
    # 20261120: the factory worker formerly named "Image builder" is the "Image assembler" (Builder CC names are reserved).
    page = page.replace("Image builder", "Image assembler").replace("image builder", "image assembler")
    encoded=json.dumps(records,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    replace('<script id="dataset"', '<script id="records" type="application/json">'+encoded+'</script><script id="dataset"')
    replace("  if(selectedLayer) layerComposition();","  if(options.path) options.path({node,wire,region,finish});\n  else if(selectedLayer) layerComposition();")
    replace("for(const g of groupNames)titles.set", "for(const [k,v] of options.names||[])titles.set(k,v);\n  for(const g of groupNames)titles.set")
    replace("build:'Assigned CC'", "build:options.path?'Build / handoff':'Assigned CC'")
    replace('Search by responsibility, capability or source symbol.</p>', "Search engine build CCs and factory capabilities by name, responsibility or source symbol.</p>'+componentAtlas.actorExample()+'")
    replace("esc(r.title)+'</strong><p class=\"cc-summary\">'", "esc(r.title)+'</strong>'+(r.workerRequirement?'<p>'+esc(r.workerRequirement)+'</p>':'')+'<div class=\"caption\">'+(r.kind==='factory'?'Artifact delivered on invocation':'Code delivered')+'</div><p class=\"cc-summary\">'")
    replace('Deliver a failing test, a scoped fix and an image that passes an independent test. Give the integration worker the completed build receipt and have the lab consume it through the existing result binding.', 'The routing worker delivers the selector change and its regression test. Source integration hands the reviewed revision to the image builder. The lab consumes the collected image and runs an independent test.')
    replace("const hay=[r.id,r.title", "const hay=[r.id,componentAtlas.ccID(r.id),r.title")
    replace("jobs.map(r=>'<a class=\"listing\" href=\"#cc/'+esc(r.id)", "jobs.map(r=>'<a class=\"listing\" href=\"#cc/'+esc(componentAtlas.ccID(r.id))")
    replace("+'<code>'+esc(r.id)+'</code><div class=\"caption\">'", "+'<code>'+esc(componentAtlas.ccID(r.id))+'</code><div class=\"caption\">'")
    replace("ccDescriptions(job.cc)+sec('Start when'", "componentAtlas.workAssignments(job)+sec('Start when'")
    start=page.index('function presentationCoverage(){')
    end=page.index('function presenterBrief()',start)
    page=page[:start]+"function presentationCoverage(){return componentAtlas.designCoverage()}\n"+page[end:]
    replace("function render(){\n const wasGraph", "function render(){\n if(componentAtlas.route())return;\n const wasGraph")
    replace(" render();\n if(saved)", " render();\n componentAtlas.normalizeLabels();\n if(saved)")
    # Install the new views before the existing router starts. Reference tabs continue to use its original handlers.
    script=source("path_stages.js")+"\n"+source("path_graph.js")+"\nconst componentAtlas=(()=>{\n"+source("atlas.js")+"\n"+source("assemblies.js")+"\n"+source("guided.js")+"\n"+source("engine_review.js")+"\n"+source("actor_views.js")+"\n"+source("construction_views.js")+"\n"+source("kinds.js")+"\n"+source("flip.js")+"\n})();\n"
    endpoint = "\n".join(source(name) for name in (
        "endpoint-data.js", "endpoint-story.js", "endpoint-map.js", "endpoint-view.js"))
    replace("const legacyNodes=",endpoint+"\n"+script+"const legacyNodes=")
    replace("</style>",source("flip.css")+"\n"+source("assemblies.css")+"\n"+source("endpoint.css")+"\n"+source("endpoint-map.css")+"\n"+source("kinds.css")+"\n</style>")
    # The catalog now filters by CC kind; the original function body is replaced by the edition's view.
    start = page.index("function library(query){")
    end = page.index("function implementationPaths(){", start)
    page = page[:start] + "function library(query){return componentAtlas.library(query)}\n" + page[end:]
    return page

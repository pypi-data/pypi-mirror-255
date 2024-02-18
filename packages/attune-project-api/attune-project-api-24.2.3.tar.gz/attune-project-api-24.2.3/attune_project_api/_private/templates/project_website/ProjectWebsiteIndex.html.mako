<%page args="projectMetadata, blueprints"/>
<!doctype html>
<html lang="en">
<%include
    file="ProjectWebsiteIndexHead.html.mako"
    args="projectMetadata=projectMetadata"/>
<body>

<!-- Project NavBar -->
<%include
    file="ProjectWebsiteIndexNavBar.html.mako"
    args="projectMetadata=projectMetadata"/>

<!-- Project Header -->
<%include
    file="ProjectWebsiteIndexHeader.html.mako"
    args="projectMetadata=projectMetadata"/>

<div class="documentation">
    <div class="container px-0">
        <div class="row">

<!-- Documentation and Instruction Sets -->
<%include
    file="ProjectWebsiteIndexBlueprintsList.html.mako"
    args="blueprints=blueprints"/>

<!-- Download Attune Ad -->
<%include
    file="ProjectWebsiteIndexAttuneAd.html.mako"/>
        </div>

<!-- Join Discord -->
<%include
    file="ProjectWebsiteIndexJoinDiscord.html.mako"/>
    </div>
</div>

<!-- Project Footer -->
<%include
    file="ProjectWebsiteIndexFooter.html.mako"
    args="projectMetadata=projectMetadata"/>

<%include
    file="ProjectWebsiteIndexScripts.html.mako"/>
</body>
</html>

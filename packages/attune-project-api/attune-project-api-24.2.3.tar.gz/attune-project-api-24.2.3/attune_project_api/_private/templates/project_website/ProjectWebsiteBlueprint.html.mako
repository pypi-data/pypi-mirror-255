<%page args="projectMetadata, blueprint, link=None, level=1, stepNum='1' "/>
<!doctype html>
<html lang="en">

<%include
file="ProjectWebsiteBlueprintHead.html.mako"
    args="blueprint=blueprint"/>

<body>

<!-- Project NavBar -->
<%include
    file="ProjectWebsiteIndexNavBar.html.mako"
    args="projectMetadata=projectMetadata"/>

<!-- Project breadcrumbs -->
<%include
file="ProjectWebsiteBlueprintBreadcrumbs.html.mako"
    args="projectMetadata=projectMetadata, blueprint=blueprint"/>

<!-- Blueprint Header -->
<%include
file="ProjectWebsiteBlueprintHeader.html.mako"
    args="blueprint=blueprint"/>

<div class="documentation">
    <div class="container px-0">
        <div class="row">

<!-- Blueprint ToC -->
<%include
file="ProjectWebsiteBlueprintToc.html.mako"
    args="blueprint=blueprint"/>

<!-- Blueprint Contents -->
            <div class="col-lg-8 pt-3">
                <div class="container">

<%include
file="ProjectWebsiteBlueprintRunWithAttune.html.mako"
    args="blueprint=blueprint"/>

<!-- Blueprint Steps -->
<%include
file="ProjectWebsiteBlueprintStep.html.mako"
    args="step=blueprint"/>
                </div>
            </div>

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
file="ProjectWebsiteBlueprintScripts.html.mako"/>

</body>
</html>

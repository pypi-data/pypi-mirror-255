<%page args="blueprint"/>

            <div class="toc col-lg-2 px-0 pr-5">
                <div class="container px-0 pt-3">
                    <p class="pb-2">
                        <strong>Contents</strong>
                    </p>
                    <p class="text-muted">
                        <a href="#top">
                            <strong>${blueprint.name}</strong>
                        </a>
                    </p>
<%include
file="ProjectWebsiteBlueprintTocInner.html.mako"
    args="step=blueprint"/>
                </div>
            </div>
<%page args="step"/>
<%namespace name="stepInnerRenderer"
file="ProjectWebsiteBlueprintStepInner.html.mako"/>
% if hasattr(step, 'links'):
    % for index, childStepLink in enumerate(step.links):
        ${stepInnerRenderer.body(step=childStepLink.step,
        link=childStepLink, stepNum=str(index + 1))}
    % endfor
% else:
        ${stepInnerRenderer.body(step=step,
        link=childStepLink)}
% endif

                    <div class="row pt-5">
                        <div class="col">
                            <h2>Completed</h2>
                            <p>
                                You have completed this instruction.
                            </p>
                        </div>
                    </div>
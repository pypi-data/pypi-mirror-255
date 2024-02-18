<%page args="step, link=None, level=0, stepNum='' "/>
<%
    stepNum = stepNum.strip('.')
    depth = stepNum.count('.') + 1

    stepName = '<strong>Step %s -</strong> %s' % (stepNum, step.name)
%>
% if level != 0:
                    <p class="text-muted pt-2">
                        <a href="#${step.key}">
                            ${stepName}
                        </a>
                    </p>
% endif
% if hasattr(step, 'links'):
    <%namespace name="tocInnerRenderer"
    file="ProjectWebsiteBlueprintTocInner.html.mako"/>
    % for index, childStepLink in enumerate(step.links):
        ${tocInnerRenderer.body(
        step=childStepLink.step,
        link=childStepLink,
        level=level+1, stepNum='%s.%s' % (stepNum, index + 1))}
    % endfor
% endif
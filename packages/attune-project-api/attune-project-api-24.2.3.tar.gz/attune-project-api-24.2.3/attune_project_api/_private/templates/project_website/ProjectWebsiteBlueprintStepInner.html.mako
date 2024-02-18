<%page args="step, link=None, headingNum=3, stepNum='1' "/>

<%
    from attune_project_api.items.step_tuples.step_tuple import (
        StepTupleTypeEnum,
        )

    stepNum = stepNum.strip('.')
    depth = stepNum.count('.') + 1

    if headingNum == 6:
        headingNum=5

    stepName = '<strong>Step %s -</strong> %s' % (stepNum, step.name)
%>

                    <div class="row pt-5">
                        <h${headingNum} id="${step.key}">
                            <a href="#${step.key}">
                                ${stepName}
                            </a>
                        </h${headingNum}>
                    </div>

% if step.comment != '':
                    <div class="row">
                        <div class="description col px-0">
                            <p>
                                ${step.makeCommentHtml(headingNum+1)}
                            </p>
                        </div>
                    </div>
% endif

<%include
file="ProjectWebsiteBlueprintStepConnection.html.mako"
    args="step=step"/>

% if step.type in (StepTupleTypeEnum.PUSH_DESIGN_FILE.value, StepTupleTypeEnum.PUSH_DESIGN_FILE_COMPILED.value):
    <%include file="ProjectWebsiteBlueprintStepFile.html.mako"
    args="step=step"/>
% elif step.type in StepTupleTypeEnum.TCP_PING.value:
    <%include file="ProjectWebsiteBlueprintStepTcpPing.html.mako"
    args="step=step"/>
% endif

% if hasattr(step, 'script') or hasattr(step, 'sql'):
    <%include
    file="ProjectWebsiteBlueprintStepScript.html.mako"
        args="step=step"/>
% endif

<%namespace name="stepInnerRenderer"
file="ProjectWebsiteBlueprintStepInner.html.mako"/>
% for index, childStepLink in enumerate(step.links if hasattr(step, 'links') else []):
    ${stepInnerRenderer.body(step=childStepLink.step, link=childStepLink,
    headingNum=headingNum+1, stepNum='%s.%s' % (stepNum, index + 1))}
% endfor

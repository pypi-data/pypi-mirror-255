<%page args="step"/>

<%

    from attune.core.steprunner.StepRunner import StepRunner
    deployPath = step.deployPath

    relative = ''
    if deployPath[0] not in ('/', '\\'):
        relative =', relative to the home directory'

    filename = step.archive.makeFileName()
%>

    <div class="row">
% if step.archive.comment != '':
        <p>
            ${step.archive.makeCommentHtml(4)}
        </p>
% endif
        <p>
            Copy the File(s)
% if hasattr(step.archive, 'remoteuri'):
            <strong><a href="${step.archive.remoteuri}">${filename}</a></strong>
% else:
            <strong>${filename}</strong>
% endif
            to the target node.
        </p>
        <p>
% if hasattr(step, 'unpack'):
    % if step.unpack:
            <strong>Extract and deploy the File(s)</strong> here:
    % else:
            <strong>Deploy the File(s)</strong> here:
    % endif
% endif
        </p>
    </div>
    <div class="row py-1">
        <code class="language-bash">
${deployPath}${relative}
        </code>
    </div>

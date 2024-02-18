<%page args="params, niceParameterNames"/>
<%text>
## Parameters
</%text>

| Name | Type | Script Reference | Comment |
| ---- | ---- | ---------------- | ------- |
% for parameter in params:
| ${parameter.name} | ${niceParameterNames[parameter.type]} | `${parameter.textName}` | ${parameter.comment.replace('\n', '<br>') if parameter.comment is not None else ''} |
% endfor

<%page args="files"/>
<%text>
## Files
</%text>
| Name | Type | Comment |
| ---- | ---- | ------- |
% for file in files:
| ${file.name} | ${file.niceName} | ${file.comment.replace('\n', '<br>') if file.comment is not None else ''} |
% endfor
